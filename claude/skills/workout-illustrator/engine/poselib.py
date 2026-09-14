"""Pose library: 26 exercise scenes for the hip/groin routine, plus helpers (A, off, seated_base).
Import the pieces you need in a project scenes.py, or reuse SCENES wholesale."""
import numpy as np
from mannequin import *

def A(p0, p1, rad=0.0, style='->', size=1.0):
    return dict(kind='arrow', p0=np.array(p0, float), p1=np.array(p1, float), rad=rad, style=style, size=size)

def off(p, dx=0, dy=0, dz=0):
    return np.array(p, float) + np.array([dx, dy, dz])

STAND_ARMS = {'uarmL': [abd('L', 8)], 'uarmR': [abd('R', 8)]}

def seated_base(hip_flex=90):
    """seated on the floor, legs straight forward"""
    return {'thighL': [flex(hip_flex)], 'thighR': [flex(hip_flex)]}

# ------------------------------------------------------------------ 1 cat-cow
def cat_cow():
    base = {'root': [pitch(-90)], 'thighL': [flex(90)], 'thighR': [flex(90)],
            'shinL': [kflex(90)], 'shinR': [kflex(90)], 'footL': [kflex(-35)], 'footR': [kflex(-35)]}
    cat = dict(base, lumbar=[tflex(-9)], thorax=[tflex(20)], neck=[tflex(32)])
    cow = dict(base, lumbar=[tflex(8)], thorax=[tflex(-17)], neck=[tflex(-32)])
    neutral = dict(base)
    Fn = Figure(neutral, root_pos=(0, 0.55, 0))
    # hands flat under the (neutral) shoulders, wrist 4 cm above floor
    targets = {s: np.array([Fn.J('shoulder' + s)[0] + 0.02, 0.045, Fn.J('shoulder' + s)[2]]) for s in 'LR'}
    def build(pose):
        F = Figure(pose, root_pos=(0, 0.55, 0))
        for s in 'LR':
            ik, phi_f = arm_ik(F, s, targets[s])
            pose = dict(pose, **ik)
            pose['hand' + s] = [('z', 90 - phi_f)]
        return Figure(pose, root_pos=(0, 0.55, 0))
    Fc = build(cat); Fw = build(cow)
    dy = -Fc.lowest(); Fc.root_pos[1] += dy; Fc.fk(); Fw.root_pos[1] += dy; Fw.fk()
    mb = Fc.J('midback')
    arrows = [A(off(mb, 0.02, 0.10, 0.22), off(mb, 0.02, 0.30, 0.22), style='<->')]
    return dict(figures=[Fc], ghosts=[Fw], props=[], cam='side', arrows=arrows, label=None)

# ------------------------------------------------------------------ 2 / 14  90-90
def ninety_ninety(lift=False):
    pose = {'thighL': [ext_rot('L', 90 + (9 if lift else 0)), flex(90)], 'shinL': [kflex(90)],
            'thighR': [abd('R', 90)], 'shinR': [kflex(90)],
            'footL': [kflex(-25)], 'footR': [kflex(-25)],
            'lumbar': [tflex(-4)],
            'uarmL': [flex(-38), abd('L', 22)], 'uarmR': [flex(-38), abd('R', 22)],
            'farmL': [eflex(12)], 'farmR': [eflex(12)],
            'handL': [eflex(-70)], 'handR': [eflex(-70)]}
    F = Figure(pose, root_pos=(0, 0.16, 0), near='L')
    F.ground()
    if lift:
        ms = F.J('midshinL')
        arrows = [A(off(ms, 0, -0.02, 0), off(ms, 0, 0.22, 0), size=0.9)]
    else:
        arrows = [A((0.66, 0.14, -0.40), (0.66, 0.14, 0.40), rad=-0.35, style='<->')]
    return dict(figures=[F], ghosts=[], props=[], cam='high2', arrows=arrows, label='viewed from above, front-left')

# ------------------------------------------------------------------ 3 glute bridge
def glute_bridge():
    a = 22
    pose = {'root': [pitch(90 + a)], 'thighL': [flex(-2)], 'thighR': [flex(-2)],
            'shinL': [kflex(92)], 'shinR': [kflex(92)], 'footL': [kflex(-22)], 'footR': [kflex(-22)],
            'uarmL': [flex(-a - 4), abd('L', 12)], 'uarmR': [flex(-a - 4), abd('R', 12)],
            'neck': [tflex(-a - 8)], 'head': []}
    F = Figure(pose, root_pos=(0, 0.33, 0))
    F.ground()
    p = F.J('pelvis')
    arrows = [A(off(p, 0.0, 0.14, 0.22), off(p, 0.0, 0.34, 0.22))]
    return dict(figures=[F], ghosts=[], props=[], cam='side', arrows=arrows, label=None)

# ------------------------------------------------------------------ 4 deep squat
def deep_squat():
    pose = {'lumbar': [tflex(28)], 'thorax': [tflex(8)], 'neck': [tflex(-18)],
            'thighL': [ext_rot('L', 18), abd('L', 26), flex(122)], 'thighR': [ext_rot('R', 18), abd('R', 26), flex(122)],
            'shinL': [kflex(142)], 'shinR': [kflex(142)], 'footL': [kflex(-18)], 'footR': [kflex(-18)],
            'uarmL': [flex(62), abd('L', 6)], 'uarmR': [flex(62), abd('R', 6)],
            'farmL': [eflex(78)], 'farmR': [eflex(78)]}
    F = Figure(pose, root_pos=(0, 0.30, 0))
    F.ground()
    kl, kr = F.J('kneeL'), F.J('kneeR')
    arrows = [A(off(kl, 0.14, 0.02, 0.16), off(kr, 0.14, 0.02, -0.16), rad=0.3, style='<->')]
    return dict(figures=[F], ghosts=[], props=[], cam='front', arrows=arrows, label=None)

# ------------------------------------------------------------------ 5 leg swings
def leg_swings():
    base = {'uarmL': [abd('L', 14)], 'uarmR': [abd('R', 58)], 'farmR': [eflex(8)],
            'footL': [kflex(-20)], 'thighR': [flex(0)]}
    fwd = dict(base, thighL=[flex(48)])
    back = dict(base, thighL=[flex(-24)])
    F = Figure(fwd, ground=False); G = Figure(back)
    # barre on far side
    hr = F.J('fingerR')
    y = hr[1]; z = hr[2] - 0.02
    props = [rod((-0.45, y, z), (0.55, y, z), 0.018, fit=False),
             rod((-0.35, 0, z), (-0.35, y, z), 0.02, fit=False), rod((0.45, 0, z), (0.45, y, z), 0.02, fit=False)]
    a0 = off(G.J('ankleL'), -0.06, -0.02, 0.12); a1 = off(F.J('ankleL'), 0.02, -0.06, 0.12)
    arrows = [A(a0, a1, rad=-0.32, style='<->')]
    return dict(figures=[F], ghosts=[G], props=props, cam='side', arrows=arrows, label=None)

# ------------------------------------------------------------------ 6 ankle circles + calf raises
def ankle_calf():
    circ = {'uarmL': [abd('L', 12)], 'uarmR': [abd('R', 12)], 'thighL': [flex(24)], 'shinL': [kflex(42)], 'footL': [kflex(10)]}
    F1 = Figure(circ, root_pos=(-0.42, 0.96, 0))
    raise_ = {'uarmL': [abd('L', 12)], 'uarmR': [abd('R', 12)], 'footL': [kflex(40)], 'footR': [kflex(40)]}
    F2 = Figure(raise_, root_pos=(0.42, 0.96, 0)); F2.ground()
    al = F1.J('ankleL')
    hl = F2.J('heelL')
    arrows = [dict(kind='circ', c=off(al, 0.06, -0.03, 0.10), r=0.13, a0=200, a1=-120, size=0.9),
              A(off(hl, -0.12, 0.0, 0.10), off(hl, -0.12, 0.26, 0.10), size=1.0)]
    return dict(figures=[F1, F2], ghosts=[], props=[], cam='side', arrows=arrows, label=None)

# ------------------------------------------------------------------ 7-9 adductor squeezes
def adductor(kind):
    if kind == 'bent':
        ab, r = 9, 0.09
        pose = {'root': [pitch(90)], 'thighL': [abd('L', ab), flex(62)], 'thighR': [abd('R', ab), flex(62)],
                'shinL': [kflex(122)], 'shinR': [kflex(122)], 'footL': [kflex(-30)], 'footR': [kflex(-30)]}
    elif kind == 'straight':
        ab, r = 5, 0.085
        pose = {'root': [pitch(90)], 'thighL': [abd('L', ab)], 'thighR': [abd('R', ab)]}
    else:
        ab, r = 24, 0.16
        pose = {'root': [pitch(90)], 'thighL': [abd('L', ab), flex(62)], 'thighR': [abd('R', ab), flex(62)],
                'shinL': [kflex(122)], 'shinR': [kflex(122)], 'footL': [kflex(-30)], 'footR': [kflex(-30)]}
    pose.update({'uarmL': [abd('L', 14)], 'uarmR': [abd('R', 14)], 'neck': [tflex(-10)]})
    F = Figure(pose, root_pos=(0, 0.11, 0)); F.ground()
    if kind == 'straight':
        jl, jr = F.J('ankleL'), F.J('ankleR')
        jl = off(jl, 0.02, 0, 0); jr = off(jr, 0.02, 0, 0)
    else:
        jl, jr = F.J('kneeL'), F.J('kneeR')
    c = (jl + jr) / 2
    props = [ball(c, r)]
    gap = (jl[2] - jr[2]) / 2
    arrows = [A(off(jl, 0, 0.0, 0.30), off(jl, 0, 0.0, 0.10), size=0.9),
              A(off(jr, 0, 0.0, -0.30), off(jr, 0, 0.0, -0.10), size=0.9)]
    return dict(figures=[F], ghosts=[], props=props, cam='high', arrows=arrows, label=None)

# ------------------------------------------------------------------ 10 / 22 copenhagen
def copenhagen(eccentric=False):
    def build(hip_y, tilt, thigh_add, bottom_abd=48):
        pose = {'root': [('z', 90), ('x', 90), ('z', -tilt)],
                'uarmL': [abd('L', 90)], 'farmL': [eflex(90)],
                'uarmR': [abd('R', -6), flex(8)], 'farmR': [eflex(70)],
                'thighR': [abd('R', -thigh_add)], 'footR': [kflex(-10)],
                'thighL': [abd('L', bottom_abd), flex(14)], 'shinL': [kflex(92)], 'footL': [kflex(-20)],
                'neck': [('x', 0)]}
        return Figure(pose, root_pos=(0, hip_y, 0), near='R')
    def foot_low(F):
        R, pw = F.T['footL']
        return min(pw[1] - 0.045, (pw + R @ np.array([0.15, -0.045, 0]))[1] - 0.035, (pw + R @ np.array([-0.04, -0.045, 0]))[1] - 0.035)
    def solve(fn, lo, hi, target, key):
        for _ in range(40):
            mid = (lo + hi) / 2
            if key(fn(mid)) < target: lo = mid
            else: hi = mid
        return (lo + hi) / 2
    BENCH_TOP = 0.50
    # hold: bottom foot on the floor
    b0 = solve(lambda a: build(0.52, 0, 4, a), 10, 70, 0.0, lambda F: -foot_low(F))
    hold = build(0.52, 0, 4, b0)
    kx = hold.J('kneeR')[0]
    props = [box((kx - 0.06, 0, -0.42), (kx + 0.70, BENCH_TOP, 0.10))]
    if not eccentric:
        p = hold.J('pelvis')
        arrows = [A(off(p, 0.0, 0.16, 0.30), off(p, 0.0, 0.36, 0.30))]
        return dict(figures=[hold], ghosts=[], props=props, cam='frontface', arrows=arrows, label=None)
    # eccentric: hips lowered, shoulder stays, knee stays on the bench, bottom foot stays on the floor
    ky = hold.J('kneeR')[1]
    HY, TILT = 0.43, 11
    ta = solve(lambda a: build(HY, TILT, a), -60, 10, -ky, lambda F: -F.J('kneeR')[1])
    b1 = solve(lambda a: build(HY, TILT, ta, a), 10, 70, 0.0, lambda F: -foot_low(F))
    low = build(HY, TILT, ta, b1)
    p0 = hold.J('pelvis'); p1 = low.J('pelvis')
    arrows = [A(off(p0, -0.02, 0.18, 0.32), off(p1, -0.02, 0.06, 0.32), rad=0.35)]
    return dict(figures=[low], ghosts=[hold], props=props, cam='frontface', arrows=arrows, label=None)

# ------------------------------------------------------------------ 11 wall psoas
def wall_psoas():
    pose = {'thighL': [flex(100)], 'shinL': [kflex(100)], 'footL': [kflex(-10)],
            'uarmL': [flex(52)], 'uarmR': [flex(52)], 'farmL': [eflex(50)], 'farmR': [eflex(50)],
            'handL': [eflex(78)], 'handR': [eflex(78)], 'thighR': [flex(0)]}
    F = Figure(pose); F.ground()
    k = F.J('kneeL')
    wx = k[0] + 0.062
    props = [box((wx, 0, -0.55), (wx + 0.12, 2.1, 0.45), fit=False)]
    arrows = [A(off(k, -0.24, 0.06, 0.12), off(k, -0.02, 0.06, 0.12))]
    return dict(figures=[F], ghosts=[], props=props, cam='sideb', arrows=arrows, label=None,
                fit_pts=[(wx + 0.12, 1.80, 0)])

# ------------------------------------------------------------------ 12 seated pelvic tilts
def pelvic_tilts():
    BLOCK = 0.13
    pose = dict(seated_base(83), lumbar=[tflex(0)],
                uarmL=[flex(-30), abd('L', 42)], farmL=[eflex(118), ('y', 60)], handL=[eflex(10)],
                uarmR=[flex(28), abd('R', 6)], farmR=[eflex(22)])
    F = Figure(pose, root_pos=(0, BLOCK + 0.10, 0))
    props = [box((-0.16, 0, -0.20), (0.14, BLOCK, 0.20))]
    p = F.J('pelvis')
    arrows = [A(off(p, 0.16, 0.16, 0.24), off(p, 0.16, -0.10, 0.24), rad=-0.5, style='<->')]
    return dict(figures=[F], ghosts=[], props=props, cam='side', arrows=arrows, label=None)

# ------------------------------------------------------------------ 13 wall pike
def wall_pike():
    pose = dict(seated_base(88), uarmL=[flex(-6), abd('L', 16)], uarmR=[flex(-6), abd('R', 16)],
                farmL=[eflex(24)], farmR=[eflex(24)], handL=[eflex(-40)], handR=[eflex(-40)])
    F = Figure(pose, root_pos=(0, 0.105, 0)); F.ground()
    wx = -0.135
    props = [box((wx - 0.12, 0, -0.55), (wx, 2.1, 0.45), fit=False)]
    p = F.J('pelvis')
    arrows = [A(off(p, 0.16, 0.04, 0.26), off(p, -0.02, 0.04, 0.26), size=0.9)]
    return dict(figures=[F], ghosts=[], props=props, cam='side', arrows=arrows, label=None,
                fit_pts=[(wx - 0.12, 1.80, 0)])

# ------------------------------------------------------------------ 15 straddle hover
def straddle_hover():
    pose = {'thighL': [abd('L', 46), flex(90)], 'thighR': [abd('R', 46), flex(90)],
            'lumbar': [tflex(8)],
            'uarmL': [flex(46), abd('L', 10)], 'uarmR': [flex(46), abd('R', 10)],
            'farmL': [eflex(8)], 'farmR': [eflex(8)], 'handL': [eflex(-50)], 'handR': [eflex(-50)]}
    F = Figure(pose, root_pos=(0, 0.11, 0)); F.ground()
    p = F.J('pelvis'); hl = F.J('heelL'); hr = F.J('heelR')
    arrows = [A(off(p, -0.16, 0.06, 0.0), off(p, -0.16, 0.30, 0.0), size=0.9),
              A(off(hl, 0.02, 0.28, 0.05), off(hl, 0.02, 0.05, 0.05), size=0.8),
              A(off(hr, 0.02, 0.28, -0.05), off(hr, 0.02, 0.05, -0.05), size=0.8)]
    return dict(figures=[F], ghosts=[], props=[], cam='high2', arrows=arrows, label='viewed from above, front-left')

# ------------------------------------------------------------------ 16 developpe
def developpe():
    base = {'uarmL': [abd('L', 70), flex(10)], 'farmL': [eflex(12)], 'uarmR': [abd('R', 58)], 'farmR': [eflex(8)],
            'thighR': [flex(0)], 'lumbar': [tflex(-4)]}
    ext = dict(base, thighL=[flex(96)], shinL=[kflex(2)], footL=[kflex(45)])
    start = dict(base, thighL=[flex(96)], shinL=[kflex(96)], footL=[kflex(45)])
    F = Figure(ext); G = Figure(start)
    hr = F.J('fingerR'); y = hr[1]; z = hr[2] - 0.02
    props = [rod((-0.45, y, z), (0.55, y, z), 0.018, fit=False),
             rod((-0.35, 0, z), (-0.35, y, z), 0.02, fit=False), rod((0.45, 0, z), (0.45, y, z), 0.02, fit=False)]
    a0 = off(G.J('ankleL'), 0.10, -0.02, 0.12); a1 = off(F.J('ankleL'), -0.06, -0.12, 0.12)
    arrows = [A(a0, a1, rad=0.4)]
    return dict(figures=[F], ghosts=[G], props=props, cam='side', arrows=arrows, label=None)

# ------------------------------------------------------------------ 17 seated good morning
def seated_good_morning():
    BLOCK = 0.13
    def build(hinge):
        pose = {'root': [pitch(-hinge)], 'thighL': [flex(83 + hinge)], 'thighR': [flex(83 + hinge)],
                'uarmL': [abd('L', 78), flex(-14)], 'uarmR': [abd('R', 78), flex(-14)],
                'farmL': [eflex(96), ('y', -10)], 'farmR': [eflex(96), ('y', 10)],
                'neck': [tflex(-4)]}
        return Figure(pose, root_pos=(0, BLOCK + 0.10, 0))
    F = build(46); G = build(0)
    nb = F.J('neckbase')
    bx = F.axis('thorax', (-0.07, -0.02, 0)); bz = F.axis('thorax', (0, 0, 1))
    c = nb + bx
    props = [box((-0.16, 0, -0.20), (0.14, BLOCK, 0.20)),
             rod(c - bz * 0.62, c + bz * 0.62, 0.016, color='band', fit=True)]
    h0 = off(G.J('head'), 0.22, 0.05, 0.1); h1 = off(F.J('head'), 0.10, 0.16, 0.1)
    arrows = [A(h0, h1, rad=0.45)]
    return dict(figures=[F], ghosts=[G], props=props, cam='side', arrows=arrows, label=None)

# ------------------------------------------------------------------ 18 jefferson curl
def jefferson():
    STEP = 0.20
    hf, lf, tf, nf = 52, 34, 40, 34
    pose = {'root': [pitch(-hf)], 'thighL': [flex(hf)], 'thighR': [flex(hf)],
            'lumbar': [tflex(lf)], 'thorax': [tflex(tf)], 'neck': [tflex(nf)],
            'uarmL': [flex(hf + lf + tf), abd('L', 4)], 'uarmR': [flex(hf + lf + tf), abd('R', 4)]}
    F = Figure(pose); F.ground(STEP)
    props = [box((-0.14, 0, -0.30), (0.32, STEP, 0.30))]
    hl, hr = F.J('fingerL'), F.J('fingerR')
    c = (hl + hr) / 2 + np.array([0, -0.02, 0])
    props.append(ball(c, 0.06, color='band'))
    nb = F.J('neckbase'); hd = F.J('head')
    arrows = [A(off(nb, 0.16, 0.14, 0.2), off(hd, 0.20, -0.16, 0.2), rad=-0.45)]
    return dict(figures=[F], ghosts=[], props=props, cam='side', arrows=arrows, label=None)

# ------------------------------------------------------------------ 19 pallof press
def pallof():
    pose = {'thighL': [abd('L', 7), flex(8)], 'thighR': [abd('R', 7), flex(8)], 'shinL': [kflex(14)], 'shinR': [kflex(14)],
            'footL': [kflex(-6)], 'footR': [kflex(-6)], 'lumbar': [tflex(4)],
            'uarmL': [flex(88), abd('L', 3)], 'uarmR': [flex(88), abd('R', 3)]}
    F = Figure(pose); F.ground()
    hl, hr = F.J('fingerL'), F.J('fingerR')
    h = (hl + hr) / 2
    anchor = np.array([h[0] - 0.05, h[1], -1.25])
    props = [rod((anchor[0], 0, anchor[2]), (anchor[0], 2.0, anchor[2]), 0.03, fit=False),
             rod(h, anchor, 0.016, color='band', fit=False),
             ball(h, 0.045, color='band')]
    arrows = [A(off(h, -0.02, 0.18, 0.0), off(h, 0.30, 0.18, 0.0))]
    return dict(figures=[F], ghosts=[], props=props, cam=(35, 45), arrows=arrows, label=None,
                fit_pts=[(anchor[0], 0.0, -0.95), (anchor[0], 1.5, -0.95)])

# ------------------------------------------------------------------ 20 side plank top leg lifted
def side_plank():
    tilt = 16.6
    pose = {'root': [('z', 90), ('x', 90), ('z', -tilt)],
            'uarmL': [abd('L', 90)], 'farmL': [eflex(90)],
            'uarmR': [abd('R', -6), flex(8)], 'farmR': [eflex(70)],
            'thighR': [abd('R', 34)], 'footR': [kflex(-10)], 'footL': [kflex(-10)]}
    F = Figure(pose, root_pos=(0, 0.40, 0), near='R'); F.ground()
    a = F.J('ankleR')
    arrows = [A(off(a, 0.0, 0.10, 0.12), off(a, 0.0, 0.32, 0.12))]
    return dict(figures=[F], ghosts=[], props=[], cam='frontface', arrows=arrows, label=None)

# ------------------------------------------------------------------ 21 dead bug
def dead_bug():
    pose = {'root': [pitch(90)], 'uarmL': [flex(88), abd('L', 4)], 'uarmR': [flex(88), abd('R', 4)],
            'thighR': [flex(90)], 'shinR': [kflex(90)], 'footR': [kflex(-10)],
            'thighL': [flex(46)], 'shinL': [kflex(100)], 'footL': [kflex(-20)],
            'neck': [tflex(-10)]}
    F = Figure(pose, root_pos=(0, 0.11, 0)); F.ground()
    h = F.J('heelL')
    arrows = [A(off(h, 0.0, 0.26, 0.10), off(h, 0.0, 0.06, 0.10), size=0.9)]
    return dict(figures=[F], ghosts=[], props=[], cam='high', arrows=arrows, label=None)

# ------------------------------------------------------------------ 23 seated fold
def seated_fold():
    hinge = 42
    pose = {'root': [pitch(-hinge)], 'thighL': [flex(89 + hinge)], 'thighR': [flex(89 + hinge)],
            'lumbar': [tflex(14)], 'thorax': [tflex(12)], 'neck': [tflex(-6)],
            'uarmL': [flex(96 + 8), abd('L', 10)], 'uarmR': [flex(96 + 8), abd('R', 10)],
            'farmL': [eflex(0)], 'farmR': [eflex(0)]}
    F = Figure(pose, root_pos=(0, 0.11, 0))
    for s in 'LR':
        tgt = F.J('toe' + s) + np.array([-0.02, 0.05, 0])
        ik, phi_f = arm_ik(F, s, tgt)
        pose.update(ik); pose['hand' + s] = [('z', 0)]
    F = Figure(pose, root_pos=(0, 0.11, 0)); F.ground()
    hl = F.J('heelL'); hd = F.J('head')
    arrows = [A(off(hl, 0.04, 0.26, 0.10), off(hl, 0.04, 0.06, 0.10), size=0.85),
              A(off(hd, -0.02, 0.22, 0.2), off(hd, 0.20, 0.10, 0.2), rad=-0.35)]
    return dict(figures=[F], ghosts=[], props=[], cam='side', arrows=arrows, label=None)

# ------------------------------------------------------------------ 24 pancake
def pancake():
    hinge = 44
    pose = {'root': [pitch(-hinge)], 'thighL': [abd('L', 50), flex(90 + hinge)], 'thighR': [abd('R', 50), flex(90 + hinge)],
            'lumbar': [tflex(8)], 'thorax': [tflex(6)], 'neck': [tflex(-8)],
            'uarmL': [flex(96 + 20), abd('L', 12)], 'uarmR': [flex(96 + 20), abd('R', 12)],
            'handL': [eflex(-40)], 'handR': [eflex(-40)]}
    F = Figure(pose, root_pos=(0, 0.11, 0)); F.ground()
    ch = F.J('chest')
    arrows = [A(off(ch, 0.0, 0.30, 0.0), off(ch, 0.26, 0.16, 0.0), rad=-0.3)]
    return dict(figures=[F], ghosts=[], props=[], cam='high', arrows=arrows, label=None)

# ------------------------------------------------------------------ 25 half frog
def half_frog():
    pose = {'root': [pitch(-90)], 'lumbar': [tflex(-18)], 'thorax': [tflex(-28)], 'neck': [tflex(-30)],
            'uarmL': [flex(102), abd('L', 6)], 'uarmR': [flex(102), abd('R', 6)],
            'farmL': [eflex(78)], 'farmR': [eflex(78)],
            'thighL': [ext_rot('L', 90), abd('L', 84)], 'shinL': [kflex(88)], 'footL': [kflex(-10)],
            'thighR': [], 'footR': [kflex(-30)]}
    F = Figure(pose, root_pos=(0, 0.12, 0)); F.ground()
    p = F.J('pelvis')
    arrows = [A(off(p, -0.02, 0.36, 0.18), off(p, -0.02, 0.14, 0.18), size=0.9)]
    return dict(figures=[F], ghosts=[], props=[], cam='high', arrows=arrows, label=None)

# ------------------------------------------------------------------ 26 couch stretch
def couch():
    pose = {'root': [pitch(10)], 'lumbar': [tflex(8)], 'thorax': [tflex(2)],
            'thighL': [flex(-12)], 'shinL': [kflex(146)], 'footL': [kflex(0)],
            'thighR': [flex(80)], 'shinR': [kflex(90)],
            'uarmL': [flex(66), abd('L', 6)], 'uarmR': [flex(66), abd('R', 6)],
            'farmL': [eflex(22)], 'farmR': [eflex(22)]}
    F = Figure(pose, root_pos=(0, 0.52, 0)); F.ground()
    kt = F.J('kneeR') + np.array([0.0, 0.08, 0])
    for s in 'LR':
        ik, phi_f = arm_ik(F, s, kt)
        pose.update(ik); pose['hand' + s] = [('z', -20)]
    F = Figure(pose, root_pos=F.root_pos)
    # couch face just behind the shin
    ms = F.J('midshinL'); ak = F.J('ankleL')
    cx = min(ms[0], ak[0]) - 0.055 - 0.015
    props = [box((cx - 0.75, 0, -0.42), (cx, 0.46, 0.40)), box((cx - 0.75, 0.46, -0.42), (cx - 0.55, 0.85, 0.40), fit=False)]
    p = F.J('pelvis')
    arrows = [A(off(p, -0.26, 0.06, 0.24), off(p, -0.10, -0.12, 0.24), rad=0.45, size=0.9)]
    return dict(figures=[F], ghosts=[], props=props, cam='side', arrows=arrows, label=None)

SCENES = [
    (1, 'Cat-cow', cat_cow),
    (2, '90/90 hip switches', lambda: ninety_ninety(False)),
    (3, 'Glute bridge', glute_bridge),
    (4, 'Deep squat rock-outs', deep_squat),
    (5, 'Leg swings', leg_swings),
    (6, 'Ankle circles + calf raises', ankle_calf),
    (7, 'Adductor squeeze, knees bent', lambda: adductor('bent')),
    (8, 'Adductor squeeze, legs straight', lambda: adductor('straight')),
    (9, 'Adductor squeeze, wide', lambda: adductor('wide')),
    (10, 'Short-lever Copenhagen hold', lambda: copenhagen(False)),
    (11, 'Wall psoas hold', wall_psoas),
    (12, 'Seated pelvic tilts', pelvic_tilts),
    (13, 'Wall pike', wall_pike),
    (14, '90/90 lift-offs', lambda: ninety_ninety(True)),
    (15, 'Straddle hover', straddle_hover),
    (16, 'Standing developpe', developpe),
    (17, 'Seated good morning', seated_good_morning),
    (18, 'Jefferson curl', jefferson),
    (19, 'Pallof press', pallof),
    (20, 'Side plank, top leg lifted', side_plank),
    (21, 'Short-lever dead bug', dead_bug),
    (22, 'Copenhagen eccentric lower', lambda: copenhagen(True)),
    (23, 'Seated fold, PNF', seated_fold),
    (24, 'Pancake hold', pancake),
    (25, 'Half-frog', half_frog),
    (26, 'Couch stretch', couch),
]
