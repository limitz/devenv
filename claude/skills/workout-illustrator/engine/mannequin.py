"""Capsule mannequin: skeleton + forward kinematics + orthographic ray-cast renderer.

World frame: figure faces +X, up is +Y, figure's LEFT is +Z.
Rotations per bone are a list of (axis, degrees) applied in order, in the parent frame.
"""
import numpy as np
from scipy.ndimage import maximum_filter, binary_dilation
from PIL import Image

# ---------------------------------------------------------------- palette
HEX = lambda h: np.array([int(h[i:i+2], 16) / 255 for i in (1, 3, 5)])
INK = HEX('#1b2a33'); MUTED = HEX('#6b7f8a'); ACCENT = HEX('#c2483a')
COL = {
    'torso': HEX('#93a8b3'),
    'head':  HEX('#93a8b3'),
    'near':  HEX('#6b7f8a'),
    'far':   HEX('#c6d2d8'),
    'prop':  HEX('#ddd8cf'),
    'prop2': HEX('#c9c2b6'),
    'ball':  HEX('#b9a48c'),
    'band':  HEX('#8a7a6a'),
    'mat':   HEX('#eaf0f2'),
}

# ---------------------------------------------------------------- rotations
def rot(axis, deg):
    t = np.radians(deg); c, s = np.cos(t), np.sin(t)
    if axis == 'x': return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == 'y': return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

def R_from(lst):
    R = np.eye(3)
    for ax, ang in lst:
        R = rot(ax, ang) @ R
    return R

# pose helpers (all return (axis, deg) tuples)
def flex(d):  return ('z', d)      # shoulder/hip flexion (+ = forward), trunk extension (+ = back)
def tflex(d): return ('z', -d)     # trunk / neck forward bend
def kflex(d): return ('z', -d)     # knee flexion
def eflex(d): return ('z', d)      # elbow flexion
def abd(side, d): return ('x', -d if side == 'L' else d)   # abduction away from midline
def ext_rot(side, d): return ('y', -d if side == 'L' else d)  # external rotation
def yaw(d): return ('y', d)
def pitch(d): return ('z', d)
def roll(d): return ('x', d)

# ---------------------------------------------------------------- skeleton
UARM, FARM, HAND = 0.29, 0.26, 0.16
THIGH, SHIN = 0.43, 0.42
BONES = {
    'root':   (None, (0, 0, 0)),
    'lumbar': ('root', (0, 0.05, 0)),
    'thorax': ('lumbar', (0, 0.20, 0)),
    'neck':   ('thorax', (0, 0.24, 0)),
    'head':   ('neck', (0, 0.07, 0)),
}
for s, z in (('L', 1), ('R', -1)):
    BONES[f'uarm{s}'] = ('thorax', (0, 0.20, 0.19 * z))
    BONES[f'farm{s}'] = (f'uarm{s}', (0, -UARM, 0))
    BONES[f'hand{s}'] = (f'farm{s}', (0, -FARM, 0))
    BONES[f'thigh{s}'] = ('root', (0, -0.03, 0.09 * z))
    BONES[f'shin{s}'] = (f'thigh{s}', (0, -THIGH, 0))
    BONES[f'foot{s}'] = (f'shin{s}', (0, -SHIN, 0))

# primitives in bone frame: ('cap', a, b, r) or ('sph', c, r); group
def bone_prims(name):
    P = []
    if name == 'root':
        P.append(('cap', (0, 0, -0.08), (0, 0, 0.08), 0.10, 'torso'))
    elif name == 'lumbar':
        for z in (-0.035, 0.035):
            P.append(('cap', (0, 0, z), (0, 0.20, z), 0.09, 'torso'))
    elif name == 'thorax':
        for z in (-0.05, 0.05):
            P.append(('cap', (0, 0, z), (0, 0.22, z), 0.10, 'torso'))
        P.append(('cap', (0, 0.20, -0.17), (0, 0.20, 0.17), 0.065, 'torso'))
    elif name == 'neck':
        P.append(('cap', (0, 0, 0), (0, 0.08, 0), 0.045, 'torso'))
    elif name == 'head':
        P.append(('sph', (0, 0.10, 0), 0.105, 'head'))
        P.append(('sph', (0.10, 0.08, 0), 0.022, 'head'))
    elif name.startswith('uarm'):
        g = 'arm' + name[-1]
        P.append(('sph', (0, 0, 0), 0.055, g))
        P.append(('cap', (0, 0, 0), (0, -UARM, 0), 0.045, g))
    elif name.startswith('farm'):
        g = 'arm' + name[-1]
        P.append(('sph', (0, 0, 0), 0.045, g))
        P.append(('cap', (0, 0, 0), (0, -FARM, 0), 0.04, g))
    elif name.startswith('hand'):
        g = 'arm' + name[-1]
        P.append(('cap', (0, 0, 0), (0, -HAND, 0), 0.035, g))
    elif name.startswith('thigh'):
        g = 'leg' + name[-1]
        P.append(('cap', (0, 0, 0), (0, -THIGH, 0), 0.075, g))
    elif name.startswith('shin'):
        g = 'leg' + name[-1]
        P.append(('sph', (0, 0, 0), 0.062, g))
        P.append(('cap', (0, 0, 0), (0, -SHIN, 0), 0.055, g))
    elif name.startswith('foot'):
        g = 'leg' + name[-1]
        P.append(('sph', (0, 0, 0), 0.045, g))
        P.append(('cap', (-0.04, -0.045, 0), (0.15, -0.045, 0), 0.035, g))
    return P

class Figure:
    """pose: dict bone -> list of (axis,deg); root_pos: world position of pelvis centre."""
    def __init__(self, pose=None, root_pos=(0, 0.96, 0), ground=False, color_override=None, near=None):
        self.pose = pose or {}
        self.near = near
        self.root_pos = np.array(root_pos, float)
        self.color_override = color_override
        self.fk()
        if ground:
            self.ground()

    def fk(self):
        self.T = {}
        for name, (parent, off) in BONES.items():
            R = R_from(self.pose.get(name, []))
            if parent is None:
                Rw = R; pw = self.root_pos.copy()
            else:
                Rp, pp = self.T[parent]
                pw = pp + Rp @ np.array(off, float)
                Rw = Rp @ R
            self.T[name] = (Rw, pw)
        self.prims = []
        for name in BONES:
            Rw, pw = self.T[name]
            for pr in bone_prims(name):
                if pr[0] == 'cap':
                    _, a, b, r, g = pr
                    self.prims.append(('cap', pw + Rw @ np.array(a, float), pw + Rw @ np.array(b, float), r, g))
                else:
                    _, c, r, g = pr
                    self.prims.append(('sph', pw + Rw @ np.array(c, float), r, g))

    def lowest(self):
        m = np.inf
        for p in self.prims:
            if p[0] == 'cap':
                m = min(m, p[1][1] - p[3], p[2][1] - p[3])
            else:
                m = min(m, p[1][1] - p[2])
        return m

    def ground(self, floor=0.0):
        dy = floor - self.lowest()
        self.root_pos[1] += dy
        self.fk()

    def J(self, name):
        """world joint positions by friendly name"""
        alias = {'pelvis': 'root', 'chest': 'thorax', 'neckbase': 'neck',
                 'hipL': 'thighL', 'hipR': 'thighR', 'kneeL': 'shinL', 'kneeR': 'shinR',
                 'ankleL': 'footL', 'ankleR': 'footR', 'shoulderL': 'uarmL', 'shoulderR': 'uarmR',
                 'elbowL': 'farmL', 'elbowR': 'farmR', 'wristL': 'handL', 'wristR': 'handR'}
        if name == 'head':
            R, p = self.T['head']; return p + R @ np.array([0, 0.10, 0])
        if name == 'headtop':
            R, p = self.T['head']; return p + R @ np.array([0, 0.205, 0])
        if name in ('toeL', 'toeR'):
            R, p = self.T['foot' + name[-1]]; return p + R @ np.array([0.15, -0.045, 0])
        if name in ('heelL', 'heelR'):
            R, p = self.T['foot' + name[-1]]; return p + R @ np.array([-0.04, -0.045, 0])
        if name in ('fingerL', 'fingerR'):
            R, p = self.T['hand' + name[-1]]; return p + R @ np.array([0, -HAND, 0])
        if name in ('midthighL', 'midthighR'):
            R, p = self.T['thigh' + name[-1]]; return p + R @ np.array([0, -THIGH / 2, 0])
        if name in ('midshinL', 'midshinR'):
            R, p = self.T['shin' + name[-1]]; return p + R @ np.array([0, -SHIN / 2, 0])
        if name == 'midback':
            R, p = self.T['thorax']; return p + R @ np.array([0, 0.05, 0])
        if name == 'lowback':
            R, p = self.T['lumbar']; return p + R @ np.array([0, 0.10, 0])
        return self.T[alias.get(name, name)][1]

    def axis(self, bone, v):
        return self.T[bone][0] @ np.array(v, float)

# ---------------------------------------------------------------- props
def box(mn, mx, color='prop', fit=True, group=None):
    return ('box', np.array(mn, float), np.array(mx, float), color, fit, group or 'prop')

def ball(c, r, color='ball', fit=True):
    return ('sph', np.array(c, float), r, color, fit, 'ball')

def rod(a, b, r, color='prop2', fit=True, group='rod'):
    return ('cap', np.array(a, float), np.array(b, float), r, color, fit, group)

# ---------------------------------------------------------------- camera
CAMS = {
    'side':  (25, 14),   # viewer on figure's left, slightly in front/above
    'sideb': (-25, 14),  # viewer on figure's left, slightly behind
    'high':  (35, 38),
    'front': (62, 18),
    'top':   (20, 62),
    'frontface': (0, 14),  # for bodies rolled to face +Z
    'frontface_high': (12, 34),
    'high2': (50, 45),
    'high45': (45, 36),
}

def camera(az, el):
    az, el = np.radians(az), np.radians(el)
    V = np.array([np.sin(az) * np.cos(el), np.sin(el), np.cos(az) * np.cos(el)])
    right = np.cross([0, 1, 0], V); right /= np.linalg.norm(right)
    up = np.cross(V, right)
    return V, right, up

# ---------------------------------------------------------------- intersections
def hit_sphere(o, d, c, r):
    oc = o - c
    B = oc @ d; C = (oc * oc).sum(1) - r * r
    h = B * B - C
    t = np.full(len(o), np.inf)
    ok = h > 0
    t[ok] = -B[ok] - np.sqrt(h[ok])
    return t

def hit_capsule(o, d, a, b, r):
    ba = b - a; oa = o - a
    baba = ba @ ba; bard = ba @ d; baoa = oa @ ba; rdoa = oa @ d; oaoa = (oa * oa).sum(1)
    A = baba - bard * bard
    if A < 1e-9:
        return np.minimum(hit_sphere(o, d, a, r), hit_sphere(o, d, b, r))
    B = baba * rdoa - baoa * bard
    C = baba * oaoa - baoa * baoa - r * r * baba
    h = B * B - A * C
    t = np.full(len(o), np.inf)
    ok = h >= 0
    sq = np.sqrt(np.where(ok, h, 0))
    tb = (-B - sq) / A
    y = baoa + tb * bard
    body = ok & (y > 0) & (y < baba)
    t[body] = tb[body]
    capm = ok & ~body
    oc = np.where((y <= 0)[:, None], oa, o - b)
    Bc = oc @ d; Cc = (oc * oc).sum(1) - r * r
    hc = Bc * Bc - Cc
    okc = capm & (hc > 0)
    tc = -Bc - np.sqrt(np.where(okc, hc, 0))
    t[okc] = tc[okc]
    return t

def normal_capsule(p, a, b, r):
    ba = b - a; pa = p - a
    h = np.clip((pa @ ba) / (ba @ ba), 0, 1)
    n = pa - h[:, None] * ba
    return n / r

def hit_box(o, d, mn, mx):
    N = len(o)
    tmin = np.full(N, -np.inf); tmax = np.full(N, np.inf); axis = np.zeros(N, int)
    for k in range(3):
        if abs(d[k]) < 1e-12:
            inside = (o[:, k] >= mn[k]) & (o[:, k] <= mx[k])
            tmax = np.where(inside, tmax, -np.inf)
            continue
        t1 = (mn[k] - o[:, k]) / d[k]; t2 = (mx[k] - o[:, k]) / d[k]
        tn = np.minimum(t1, t2); tf = np.maximum(t1, t2)
        upd = tn > tmin
        axis = np.where(upd, k, axis)
        tmin = np.maximum(tmin, tn); tmax = np.minimum(tmax, tf)
    ok = (tmax >= tmin) & (tmax > 0) & (tmin > 0)
    t = np.where(ok, tmin, np.inf)
    return t, axis

# ---------------------------------------------------------------- renderer
class Render:
    pass

def render_scene(figures, props=(), cam='side', W=1020, H=740, ss=2, margin=0.07,
                 mat=True, mat_pad=0.16, fit_pts=None, ghost_figures=(), scale_lock=None):
    """Returns Render with .rgba (H,W,4 float), .project(p)->(x,y) px, .mask_ghost etc."""
    az, el = CAMS[cam] if isinstance(cam, str) else cam
    V, right, up = camera(az, el)
    d = -V
    # collect prims
    prims = []   # (kind, ..., color_key, group_id, outline_color)
    gid = 0
    fit = []
    nearside = {}
    for fi, F in enumerate(figures):
        # near/far: compare depth of hips
        zl = F.J('hipL') @ V; zr = F.J('hipR') @ V
        near = F.near or ('L' if zl >= zr else 'R')
        for pr in F.prims:
            g = pr[-1]
            if g in ('torso', 'head'):
                ck = g
            else:
                ck = 'near' if g[-1] == near else 'far'
            if F.color_override:
                ck = F.color_override
            gname = f'f{fi}:{g}'
            prims.append((pr, ck, gname))
            if pr[0] == 'cap':
                fit += [pr[1] + right * pr[3], pr[1] - right * pr[3], pr[1] + up * pr[3], pr[1] - up * pr[3],
                        pr[2] + right * pr[3], pr[2] - right * pr[3], pr[2] + up * pr[3], pr[2] - up * pr[3]]
            else:
                fit += [pr[1] + right * pr[2], pr[1] - right * pr[2], pr[1] + up * pr[2], pr[1] - up * pr[2]]
    for pr in props:
        kind = pr[0]
        if kind == 'box':
            _, mn, mx, ck, dofit, g = pr
            prims.append((('box', mn, mx, g), ck, 'p:' + g))
            if dofit:
                for cx in (mn[0], mx[0]):
                    for cy in (mn[1], mx[1]):
                        for cz in (mn[2], mx[2]):
                            fit.append(np.array([cx, cy, cz]))
        elif kind == 'sph':
            _, c, r, ck, dofit, g = pr
            prims.append((('sph', c, r, g), ck, 'p:' + g))
            if dofit:
                fit += [c + right * r, c - right * r, c + up * r, c - up * r]
        elif kind == 'cap':
            _, a, b, r, ck, dofit, g = pr
            prims.append((('cap', a, b, r, g), ck, 'p:' + g))
            if dofit:
                fit += [a + right * r, a - right * r, a + up * r, a - up * r,
                        b + right * r, b - right * r, b + up * r, b - up * r]
    if fit_pts is not None:
        fit += [np.array(p, float) for p in fit_pts]
    # ghost figures contribute to fit but not to the main render
    for F in ghost_figures:
        for pr in F.prims:
            if pr[0] == 'cap':
                fit += [pr[1] + up * pr[3], pr[1] - up * pr[3], pr[2] + up * pr[3], pr[2] - up * pr[3],
                        pr[1] + right * pr[3], pr[1] - right * pr[3], pr[2] + right * pr[3], pr[2] - right * pr[3]]
            else:
                fit += [pr[1] + up * pr[2], pr[1] - up * pr[2], pr[1] + right * pr[2], pr[1] - right * pr[2]]
    fit = np.array(fit)
    us = fit @ right; vs = fit @ up
    u0, u1, v0, v1 = us.min(), us.max(), vs.min(), vs.max()
    bw, bh = (u1 - u0) * (1 + 2 * margin), (v1 - v0) * (1 + 2 * margin)
    scale = min(W / bw, H / bh)  # px per metre (final res)
    if scale_lock:
        scale = min(scale, scale_lock)
    uc, vc = (u0 + u1) / 2, (v0 + v1) / 2
    # mat
    if mat:
        allp = []
        for F in list(figures) + list(ghost_figures):
            for pr in F.prims:
                allp.append(pr[1]); allp.append(pr[2] if pr[0] == 'cap' else pr[1])
        allp = np.array(allp)
        mn = np.array([allp[:, 0].min() - mat_pad, -0.012, allp[:, 2].min() - mat_pad])
        mx = np.array([allp[:, 0].max() + mat_pad, 0.0, allp[:, 2].max() + mat_pad])
        prims.append((('box', mn, mx, 'mat'), 'mat', 'p:mat'))
        for cx in (mn[0], mx[0]):
            for cz in (mn[2], mx[2]):
                fit = np.vstack([fit, [[cx, 0.0, cz]]])
        us = fit @ right; vs = fit @ up
        u0, u1, v0, v1 = us.min(), us.max(), vs.min(), vs.max()
        bw, bh = (u1 - u0) * (1 + 2 * margin), (v1 - v0) * (1 + 2 * margin)
        scale = min(W / bw, H / bh)
        uc, vc = (u0 + u1) / 2, (v0 + v1) / 2
    # pixel grid (supersampled)
    Ws, Hs = W * ss, H * ss
    sc = scale * ss
    ii, jj = np.meshgrid(np.arange(Ws), np.arange(Hs))
    u = (ii + 0.5 - Ws / 2) / sc + uc
    v = (Hs / 2 - (jj + 0.5)) / sc + vc
    origin = (u[..., None] * right + v[..., None] * up + 6.0 * V)
    depth = np.full((Hs, Ws), np.inf)
    idmap = np.full((Hs, Ws), -1, int)
    normal = np.zeros((Hs, Ws, 3))
    meta = []
    def px_bbox(pts, r):
        pts = np.atleast_2d(pts)
        uu = pts @ right; vv = pts @ up
        x0 = int(np.floor((uu.min() - r - uc) * sc + Ws / 2)) - 1
        x1 = int(np.ceil((uu.max() + r - uc) * sc + Ws / 2)) + 1
        y0 = int(np.floor(Hs / 2 - (vv.max() + r - vc) * sc)) - 1
        y1 = int(np.ceil(Hs / 2 - (vv.min() - r - vc) * sc)) + 1
        return max(x0, 0), min(x1, Ws), max(y0, 0), min(y1, Hs)
    for k, (pr, ck, gname) in enumerate(prims):
        kind = pr[0]
        if kind == 'box':
            _, mn, mx, g = pr
            corners = np.array([[x, y, z] for x in (mn[0], mx[0]) for y in (mn[1], mx[1]) for z in (mn[2], mx[2])])
            x0, x1, y0, y1 = px_bbox(corners, 0)
        elif kind == 'sph':
            x0, x1, y0, y1 = px_bbox(pr[1], pr[2])
        else:
            x0, x1, y0, y1 = px_bbox(np.array([pr[1], pr[2]]), pr[3])
        if x1 <= x0 or y1 <= y0:
            meta.append((ck, gname)); continue
        o = origin[y0:y1, x0:x1].reshape(-1, 3)
        if kind == 'box':
            t, ax = hit_box(o, d, mn, mx)
        elif kind == 'sph':
            t = hit_sphere(o, d, pr[1], pr[2])
        else:
            t = hit_capsule(o, d, pr[1], pr[2], pr[3])
        sub_d = depth[y0:y1, x0:x1].reshape(-1)
        upd = t < sub_d
        if upd.any():
            p = o[upd] + t[upd, None] * d
            if kind == 'box':
                n = np.zeros((upd.sum(), 3))
                axs = ax[upd]
                for a_ in range(3):
                    n[axs == a_, a_] = -np.sign(d[a_]) if abs(d[a_]) > 1e-12 else 1
            elif kind == 'sph':
                n = (p - pr[1]) / pr[2]
            else:
                n = normal_capsule(p, pr[1], pr[2], pr[3])
            sub_d[upd] = t[upd]
            depth[y0:y1, x0:x1] = sub_d.reshape(y1 - y0, x1 - x0)
            sub_id = idmap[y0:y1, x0:x1].reshape(-1); sub_id[upd] = k
            idmap[y0:y1, x0:x1] = sub_id.reshape(y1 - y0, x1 - x0)
            sub_n = normal[y0:y1, x0:x1].reshape(-1, 3); sub_n[upd] = n
            normal[y0:y1, x0:x1] = sub_n.reshape(y1 - y0, x1 - x0, 3)
        meta.append((ck, gname))
    # shading
    L = right * 0.35 + up * 0.75 + V * 0.55; L /= np.linalg.norm(L)
    ndl = normal @ L
    rgb = np.zeros((Hs, Ws, 3)); alpha = np.zeros((Hs, Ws))
    hit = idmap >= 0
    colkeys = np.array([m[0] for m in meta] + ['mat'])
    groups = [m[1] for m in meta] + ['p:mat']
    base = np.zeros((Hs, Ws, 3))
    for k, (ck, gname) in enumerate(meta):
        m = idmap == k
        if not m.any():
            continue
        base[m] = COL[ck]
    # contact shadow on mat and box tops: darken points under low body parts
    shade = np.where(ndl > 0.2, 1.0, 0.80)
    shade = np.where(ndl > 0.72, 1.06, shade)
    # mat/box pixels: flat, but with contact shadow
    isprop = np.zeros((Hs, Ws), bool)
    for k, (ck, gname) in enumerate(meta):
        if gname.startswith('p:'):
            isprop |= idmap == k
    shade = np.where(isprop, np.where(ndl > 0.5, 1.0, 0.88), shade)
    # contact shadow
    P = origin + depth[..., None] * d
    shadow = np.zeros((Hs, Ws))
    floorpix = isprop & (np.abs(normal[..., 1] - 1) < 1e-3)
    if floorpix.any():
        fp = P[floorpix]
        sh = np.zeros(len(fp))
        for F in figures:
            for pr in F.prims:
                if pr[0] == 'cap':
                    a, b, r = pr[1], pr[2], pr[3]
                else:
                    a = b = pr[1]; r = pr[2]
                hmin = min(a[1], b[1]) - r
                a2 = np.array([a[0], a[2]]); b2 = np.array([b[0], b[2]])
                ba = b2 - a2; l2 = ba @ ba
                q = fp[:, [0, 2]] - a2
                hh = np.clip((q @ ba) / l2, 0, 1) if l2 > 1e-9 else np.zeros(len(q))
                dist = np.linalg.norm(q - hh[:, None] * ba, axis=1) - r
                # height of that point on the capsule above the floor surface
                ys = a[1] + hh * (b[1] - a[1]) - r - fp[:, 1]
                s = np.clip(1 - dist / 0.06, 0, 1) * np.clip(1 - ys / 0.20, 0, 1)
                sh = np.maximum(sh, s)
        shadow[floorpix] = sh
    shade = shade * (1 - 0.16 * shadow)
    rgb = base * shade[..., None]
    alpha[hit] = 1.0
    # outlines
    far_ids = np.array([ck == 'far' for ck, g in meta] + [False])
    edge = np.zeros((Hs, Ws), bool)
    edge_far = np.zeros((Hs, Ws), bool)
    dep = np.where(np.isinf(depth), 1e3, depth)
    for dy, dx in ((0, 1), (1, 0)):
        a_id = idmap[:Hs - dy, :Ws - dx]; b_id = idmap[dy:, dx:]
        a_d = dep[:Hs - dy, :Ws - dx]; b_d = dep[dy:, dx:]
        ga = np.array(groups)[a_id]; gb = np.array(groups)[b_id]
        diff = (ga != gb) | (np.abs(a_d - b_d) > 0.03)
        e = np.zeros((Hs, Ws), bool)
        e[:Hs - dy, :Ws - dx] |= diff
        e[dy:, dx:] |= diff
        edge |= e
        # far-limb outline: both sides are far or background
        fa = far_ids[a_id] | (a_id < 0); fb = far_ids[b_id] | (b_id < 0)
        farboth = diff & fa & fb & ~((a_id < 0) & (b_id < 0))
        ef = np.zeros((Hs, Ws), bool)
        ef[:Hs - dy, :Ws - dx] |= farboth; ef[dy:, dx:] |= farboth
        edge_far |= ef
    k = int(round(2.5 * ss))
    yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
    disc = (xx ** 2 + yy ** 2) <= k * k
    edge_d = binary_dilation(edge, structure=disc)
    edge_far_d = binary_dilation(edge_far, structure=disc) & ~binary_dilation(edge & ~edge_far, structure=disc)
    line_col = np.where(edge_far_d[..., None], MUTED, INK)
    rgb = np.where(edge_d[..., None], line_col, rgb)
    alpha = np.where(edge_d, 1.0, alpha)
    rgba = np.concatenate([rgb, alpha[..., None]], axis=-1)
    # downsample
    img = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA')
    img = img.resize((W, H), Image.LANCZOS)
    R = Render()
    R.img = img
    R.W, R.H = W, H
    R.scale, R.uc, R.vc, R.right, R.up, R.V = scale, uc, vc, right, up, V
    R.mask = np.array(img)[..., 3] > 8
    def project(p):
        p = np.asarray(p, float)
        uu = p @ right; vv = p @ up
        return ((uu - uc) * scale + W / 2, H / 2 - (vv - vc) * scale)
    R.project = project
    R.silhouette_of = lambda figs: silhouette(figs, R, ss)
    return R

def silhouette(figs, R, ss=2):
    """Binary mask (H,W) of figures at the same camera as R (for ghost outlines)."""
    right, up, V, scale, uc, vc, W, H = R.right, R.up, R.V, R.scale, R.uc, R.vc, R.W, R.H
    d = -V
    ii, jj = np.meshgrid(np.arange(W), np.arange(H))
    u = (ii + 0.5 - W / 2) / scale + uc
    v = (H / 2 - (jj + 0.5)) / scale + vc
    origin = (u[..., None] * right + v[..., None] * up + 6.0 * V).reshape(-1, 3)
    m = np.zeros(W * H, bool)
    for F in figs:
        for pr in F.prims:
            if pr[0] == 'cap':
                t = hit_capsule(origin, d, pr[1], pr[2], pr[3])
            else:
                t = hit_sphere(origin, d, pr[1], pr[2])
            m |= np.isfinite(t)
    return m.reshape(H, W)

# ---------------------------------------------------------------- 2-link IK in the sagittal plane
def _ang(R):
    """world rotation angle about Z of a frame (valid for sagittal-plane poses)"""
    return np.degrees(np.arctan2(R[1, 0], R[0, 0]))

def arm_ik(F, side, target, elbow_sign=1):
    """Return dict of pose entries for uarm/farm so the wrist lands on target (x,y used).
    Assumes the arm moves in the sagittal plane; elbow bends forward for elbow_sign=+1."""
    S = F.J('shoulder' + side); T = np.asarray(target, float)
    d = T - S; L = float(np.hypot(d[0], d[1])); L = min(L, UARM + FARM - 1e-3)
    e = np.degrees(np.arccos(np.clip((UARM**2 + FARM**2 - L**2) / (2 * UARM * FARM), -1, 1)))
    a = np.degrees(np.arccos(np.clip((UARM**2 + L**2 - FARM**2) / (2 * UARM * L), -1, 1)))
    phi_T = np.degrees(np.arctan2(d[0], -d[1]))
    phi_u = phi_T - elbow_sign * a
    eflex_ = elbow_sign * (180 - e)
    phi_f = phi_u + eflex_
    thorax_ang = _ang(F.T['thorax'][0])
    return {'uarm' + side: [('z', phi_u - thorax_ang)], 'farm' + side: [('z', eflex_)]}, phi_f

def leg_ik(F, side, target, knee_sign=1):
    """Thigh/shin angles so the ankle lands on target (sagittal plane). Knee bends backward for knee_sign=+1."""
    Hp = F.J('hip' + side); T = np.asarray(target, float)
    d = T - Hp; L = float(np.hypot(d[0], d[1])); L = min(L, THIGH + SHIN - 1e-3)
    e = np.degrees(np.arccos(np.clip((THIGH**2 + SHIN**2 - L**2) / (2 * THIGH * SHIN), -1, 1)))
    a = np.degrees(np.arccos(np.clip((THIGH**2 + L**2 - SHIN**2) / (2 * THIGH * L), -1, 1)))
    phi_T = np.degrees(np.arctan2(d[0], -d[1]))
    phi_t = phi_T + knee_sign * a
    kflex_ = knee_sign * (180 - e)
    root_ang = _ang(F.T['root'][0])
    return {'thigh' + side: [('z', phi_t - root_ang)], 'shin' + side: [('z', -kflex_)]}, phi_t - kflex_
