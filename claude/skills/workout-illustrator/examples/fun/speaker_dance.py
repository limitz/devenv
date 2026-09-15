"""Just for fun: a ballet opening, a feminine phrase, a twerk with the back to the audience, then the
dancer spots a block, walks up, kicks it, finds out the hard way that it is a speaker cabinet,
hops holding the foot and limps off.
usage: python3 speaker_dance.py [out.gif] [--sheet sheet.png] [--check] [--draft] [--workers N]"""
import sys, os
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import numpy as np
from mannequin import *
from animate import sequence, param_pose, _caption

# ---------------------------------------------------------------- figure
def build(p):
    pose = param_pose(p)
    # body-frame pitch/roll (innermost, before yaw) so a turned figure can still tilt its own pelvis
    pose['root'] = [('z', p.get('bpitch', 0.0)), ('x', p.get('broll', 0.0))] + pose['root']
    F = Figure(pose, root_pos=(p.get('x', 0.0), 0.96, p.get('z', 0.0)))
    F.ground()                     # sequence() smooths the height afterwards
    return F

def grounded_height(p):
    F = build({k: v for k, v in p.items() if k not in ('rooty', 'label')}); return float(F.root_pos[1])

def arm(side, flex=0, abd=0, elbow=0, rot=0):
    return {'uflex' + side: flex, 'uabd' + side: abd, 'elbow' + side: elbow, 'urot' + side: rot}
def leg(side, flex=0, abd=0, knee=0, foot=0, rot=0):
    return {'tflex' + side: flex, 'tabd' + side: abd, 'knee' + side: knee, 'foot' + side: foot, 'trot' + side: rot}
def M(*ds, **kw):
    q = {}
    for d in ds: q.update(d)
    q.update(kw); return q

# ---------------------------------------------------------------- the block that is a speaker
SPK_X0, SPK_X1, SPK_H, SPK_Z0, SPK_Z1 = 1.45, 1.79, 0.48, -0.17, 0.17
COL['speaker'] = HEX('#343a42'); COL['cone'] = HEX('#5e5449')
SPK_CX = (SPK_X0 + SPK_X1) / 2
PROPS = [box((-1.2, -0.012, -0.8), (2.1, 0.0, 1.1), color='mat', fit=False, group='mat'),
         box((SPK_X0, 0, SPK_Z0), (SPK_X1, SPK_H, SPK_Z1), color='speaker', fit=True, group='spk'),
         # cones on the face the audience sees (+Z): shallow spherical caps poking out of the cabinet
         ball((SPK_CX, 0.19, SPK_Z1 - 0.125), 0.14, color='cone', fit=False),
         ball((SPK_CX, 0.38, SPK_Z1 - 0.05), 0.06, color='cone', fit=False)]

# ---------------------------------------------------------------- ballet vocabulary (from ballet.py)
TURNOUT = 55
def legs(**kw):
    q = dict(trotL=TURNOUT, trotR=TURNOUT); q.update(kw); return q
BRAS_BAS = dict(uabdL=22, uabdR=22, uflexL=14, uflexR=14, elbowL=24, elbowR=24)
FIRST = dict(uabdL=16, uabdR=16, uflexL=52, uflexR=52, elbowL=62, elbowR=62)
SECOND = dict(uabdL=82, uabdR=82, uflexL=12, uflexR=12, elbowL=18, elbowR=18)
EN_HAUT_L = dict(uflexL=155, uabdL=30, elbowL=36)
fifth = legs(tflexR=4, tabdR=-14, tflexL=-4, tabdL=-4)                       # right foot front, crossed
plie = M(fifth, kneeL=48, kneeR=48, tflexL=20, tflexR=28)
retire = legs(tflexL=0, footL=50, trotR=62, tabdR=42, tflexR=58, kneeR=126, footR=45)     # right leg retire, left on demi-pointe
seconde = M(legs(tflexL=0, footL=50, trotR=60, tabdR=88, tflexR=6, kneeR=0, footR=45), lumbarside=9, neckside=-8)
bour1 = M(legs(tflexR=-16, tabdR=2, footR=48, tflexL=2, tabdL=-2, footL=48))
bour2 = M(legs(tflexL=0, tabdL=24, footL=48, tflexR=-4, tabdR=2, footR=48))
bour3 = M(legs(tflexR=22, tabdR=-7, kneeR=42, tflexL=14, tabdL=2, kneeL=42))
prep = M(legs(tflexR=-26, tabdR=-4, tflexL=24, kneeL=46, tabdL=-2), FIRST, uabdL=82, uflexL=12, elbowL=18)
finish = M(legs(tflexR=-26, tabdR=-4, kneeR=30, tflexL=24, kneeL=48, tabdL=-2), SECOND)

# ---------------------------------------------------------------- feminine phrase (styling from lyrical.py)
swayL = M(**leg('L', flex=4, abd=8, knee=6), **leg('R', flex=8, abd=10, knee=22, foot=10), broll=7, lumbarside=-8,
          thoraxside=-3, neckside=9, **arm('L', flex=14, abd=24, elbow=30), **arm('R', flex=150, abd=28, elbow=28))
swayR = M(**leg('R', flex=4, abd=8, knee=6), **leg('L', flex=8, abd=10, knee=22, foot=10), broll=-7, lumbarside=8,
          thoraxside=3, neckside=-9, **arm('R', flex=14, abd=24, elbow=30), **arm('L', flex=150, abd=28, elbow=28))
base_legs = M(**leg('L', flex=6, abd=9, knee=12), **leg('R', flex=6, abd=9, knee=12))
flip1 = M(base_legs, neck=20, neckside=-14, neckyaw=-12, lumbarside=4, **arm('R', flex=150, abd=26, elbow=128, rot=20),
          **arm('L', flex=4, abd=22, elbow=12))
flip2 = M(base_legs, neck=-18, neckside=14, thorax=-12, lumbarside=-9, broll=5, **arm('R', flex=140, abd=85, elbow=12),
          **arm('L', flex=-10, abd=24, elbow=10))
wave1 = M(base_legs, lumbar=22, thorax=-6, neck=14, **arm('L', flex=10, abd=40, elbow=20), **arm('R', flex=10, abd=40, elbow=20))
wave2 = M(base_legs, lumbar=-14, thorax=20, neck=4, **arm('L', flex=30, abd=60, elbow=25), **arm('R', flex=30, abd=60, elbow=25))
wave3 = M(base_legs, lumbar=2, thorax=-18, neck=-14, **arm('L', flex=40, abd=92, elbow=10), **arm('R', flex=40, abd=92, elbow=10))
HIPS = M(**arm('L', flex=-12, abd=34, elbow=105, rot=-70), **arm('R', flex=-12, abd=34, elbow=105, rot=-70))
hip_legs = M(**leg('L', flex=8, abd=12, knee=14), **leg('R', flex=8, abd=12, knee=14))
circ = [M(hip_legs, HIPS, broll=-8, lumbarside=8, neckside=4), M(hip_legs, HIPS, bpitch=-7, lumbar=9, neck=-4),
        M(hip_legs, HIPS, broll=8, lumbarside=-8, neckside=-4), M(hip_legs, HIPS, bpitch=7, lumbar=-8, neck=4)]
def stride(front):
    back = 'R' if front == 'L' else 'L'
    return M(**leg(front, flex=26, abd=6, knee=8, foot=-6), **leg(back, flex=-14, abd=6, knee=14, foot=18),
             broll=6 if front == 'L' else -6, lumbarside=-7 if front == 'L' else 7, lumbartwist=-10 if front == 'L' else 10,
             **arm(back, flex=28, abd=12, elbow=22), **arm(front, flex=-22, abd=12, elbow=22), neckside=0)
glance = M(**leg('L', flex=2, abd=6, knee=4), **leg('R', flex=10, abd=14, knee=26, foot=8), broll=-6, lumbarside=11, thoraxside=-4,
           neckyaw=-45, neckside=6, **arm('R', flex=-12, abd=34, elbow=105, rot=-70), **arm('L', flex=6, abd=16, elbow=10))

# ---------------------------------------------------------------- twerk (back to the audience, yaw 460)
TW = M(**leg('L', flex=56, abd=24, knee=72, rot=14), **leg('R', flex=56, abd=24, knee=72, rot=14), lumbar=44, thorax=14, neck=-24)
# hands to the knees: sagittal 2-link IK on the un-yawed figure, then a little abduction so the arms clear the thighs
_F = build(TW)
for _s in 'LR':
    _k = _F.J('knee' + _s); _ik, _ = arm_ik(_F, _s, _k + np.array([0.07, 0.10, 0]))
    TW['uflex' + _s] = _ik['uarm' + _s][0][1]; TW['elbow' + _s] = _ik['farm' + _s][0][1]; TW['uabd' + _s] = 10
def tilt(base, d, dk):
    """anterior pelvic tilt by d degrees (hips up and back) with the trunk and feet compensated; dk = extra knee bend"""
    q = dict(base); q['bpitch'] = base.get('bpitch', 0.0) - d; q['lumbar'] = base['lumbar'] - d
    for s in 'LR':
        q['tflex' + s] += d; q['knee' + s] += dk
    return q
TW_UP, TW_DOWN = tilt(TW, 16, -14), tilt(TW, -10, 14)
SHAKE = M(TW, lumbar=36, **arm('R', flex=150, abd=38, elbow=14))
SHAKE_L = M(SHAKE, broll=10, lumbarside=-9, neckside=-4)
SHAKE_R = M(SHAKE, broll=-10, lumbarside=9, neckside=4)

# ---------------------------------------------------------------- the block
STAND = M(**leg('L', abd=6, knee=3), **leg('R', abd=6, knee=3), **arm('L', abd=8, elbow=8), **arm('R', abd=8, elbow=8))
SPOT = M(STAND, lumbar=10, neck=-6, **arm('R', flex=158, abd=6, elbow=132, rot=10), **arm('L', abd=10, elbow=8))
def walk(front, x):
    back = 'R' if front == 'L' else 'L'
    return M(**leg(front, flex=22, abd=6, knee=6, foot=-6), **leg(back, flex=-12, abd=6, knee=12, foot=16),
             **arm(back, flex=24, abd=10, elbow=18), **arm(front, flex=-18, abd=10, elbow=18), lumbar=6, x=x)
READY = M(STAND, kneeL=8, kneeR=8, lumbar=4, **arm('L', flex=30, abd=14, elbow=100), **arm('R', flex=30, abd=14, elbow=100))
WINDUP = M(**leg('L', flex=4, abd=8, knee=14), **leg('R', flex=78, abd=6, knee=124, foot=20), lumbar=-8, thorax=-4,
           **arm('L', flex=50, abd=18, elbow=90), **arm('R', flex=-20, abd=22, elbow=95))
KICK = M(**leg('L', flex=0, abd=8, knee=6), **leg('R', flex=47, abd=4, knee=3, foot=-16), lumbar=-14, thorax=-4, bpitch=4,
         **arm('L', flex=-30, abd=26, elbow=40), **arm('R', flex=60, abd=26, elbow=60))
_toe = build(M(KICK, x=0.0)).J('toeR')
X_KICK = SPK_X0 - _toe[0] - FOOT_R - 0.004                     # pelvis x that puts the toe on the cabinet face
RECOIL = M(**leg('L', flex=8, abd=10, knee=22), **leg('R', flex=62, abd=10, knee=96, foot=10), lumbar=8, thorax=-10, neck=-10, bpitch=10,
           **arm('L', flex=110, abd=60, elbow=30), **arm('R', flex=110, abd=60, elbow=30))
GRAB = M(**leg('L', flex=6, abd=8, knee=12), **leg('R', flex=88, abd=16, knee=128, foot=30, rot=20), lumbar=32, thorax=12, neck=26,
         **arm('L', flex=66, abd=14, elbow=58), **arm('R', flex=62, abd=14, elbow=62))
GRAB_HOP = M(GRAB, kneeL=6, footL=30)
LIMP_BAD = M(**leg('R', flex=16, abd=8, knee=30, foot=40), **leg('L', flex=-10, abd=8, knee=10, foot=8), lumbar=26, thorax=6, neck=10,
             lumbarside=-14, broll=-5, **arm('L', flex=20, abd=80, elbow=18), **arm('R', flex=40, abd=70, elbow=40))
LIMP_GOOD = M(**leg('L', flex=26, abd=8, knee=10, foot=-4), **leg('R', flex=-4, abd=8, knee=40, foot=42), lumbar=16, thorax=4, neck=12,
              lumbarside=10, broll=6, **arm('L', flex=-10, abd=70, elbow=20), **arm('R', flex=30, abd=85, elbow=30))
TURN_AWAY = M(**leg('L', flex=4, abd=8, knee=8), **leg('R', flex=10, abd=10, knee=34, foot=42), lumbar=24, neck=14, lumbarside=-6,
              **arm('L', flex=10, abd=60, elbow=20), **arm('R', flex=50, abd=50, elbow=50))

# ---------------------------------------------------------------- timeline
K = []
_state = dict(x=0.0, z=0.0, yaw=0.0)
def kf(t, pose, label=None, **pos):
    """append a keyframe; x / z / yaw carry over from the previous keyframe unless given"""
    for k_ in ('x', 'z', 'yaw'):
        if k_ in pose: _state[k_] = pose[k_]
    _state.update(pos)
    q = dict(pose); q.update(_state)
    if label: q['label'] = label
    K.append((t, q))

# ballet
kf(0.0, M(fifth, BRAS_BAS), 'fifth position, bras bas')
kf(0.5, M(fifth, BRAS_BAS))
kf(1.0, M(plie, FIRST), 'demi-plié')
kf(1.5, M(retire, FIRST), 'développé à la seconde')
kf(2.1, M(seconde, SECOND, EN_HAUT_L))
kf(2.6, M(seconde, SECOND, EN_HAUT_L))
kf(3.1, M(fifth, BRAS_BAS), 'close in fifth')
kf(3.5, M(bour1, FIRST), 'pas de bourrée', x=-0.06, z=0.1)
kf(3.85, M(bour2, SECOND), x=-0.02, z=0.2)
kf(4.2, M(bour3, FIRST), x=0.0, z=0.3)
kf(4.7, prep, 'preparation in fourth')
kf(5.05, M(retire, FIRST), 'pirouette en dehors', yaw=0)
kf(5.3, M(retire, FIRST), yaw=150)
kf(5.85, M(retire, FIRST), yaw=340)
kf(6.15, M(retire, FIRST), yaw=360)
kf(6.5, finish, 'finish in fourth')
kf(6.9, finish)
# feminine phrase
kf(7.2, swayL, 'hip sway')
kf(7.9, swayR)
kf(8.5, swayL)
kf(9.0, flip1, 'hair flip')
kf(9.4, flip2)
kf(9.8, M(flip2, neck=-8, neckside=8))
kf(10.2, wave1, 'body wave')
kf(10.6, wave2)
kf(11.0, wave3)
kf(11.5, circ[0], 'hip circle, hands on hips')
kf(11.8, circ[1]); kf(12.1, circ[2]); kf(12.4, circ[3]); kf(12.7, circ[0])
kf(13.1, stride('L'), 'sassy walk', x=0.10, z=0.2)
kf(13.5, stride('R'), x=0.20, z=0.1)
kf(13.9, stride('L'), x=0.30, z=0.0)
kf(14.3, glance, 'a glance at the audience', x=0.34)
kf(14.8, glance, 'turn around…')
# twerk
kf(15.3, TW, 'twerk', yaw=460)
for i, t in enumerate(np.arange(15.5, 17.2, 0.2)):
    kf(round(float(t), 2), TW_UP if i % 2 == 0 else TW_DOWN)
kf(17.4, SHAKE, 'hip shake')
for i, t in enumerate(np.arange(17.6, 18.7, 0.2)):
    kf(round(float(t), 2), SHAKE_L if i % 2 == 0 else SHAKE_R)
kf(19.0, STAND, '…hm?', yaw=360)
# the block
kf(19.3, SPOT, '…a block?')
kf(19.9, SPOT)
kf(20.2, walk('L', 0.34 + (X_KICK - 0.34) * 0.5))
kf(20.5, walk('R', X_KICK))
kf(20.75, READY)
kf(21.0, WINDUP, 'kick it!')
kf(21.18, KICK)
kf(21.28, KICK)
kf(21.5, RECOIL, 'CLONK.', x=X_KICK - 0.08)
kf(21.9, GRAB, '…it is a speaker.')
for i, t in enumerate(np.arange(22.2, 23.3, 0.2)):
    q = dict(GRAB_HOP)
    if i % 2 == 0: q['rooty'] = grounded_height(M(GRAB_HOP, **_state)) + 0.11
    kf(round(float(t), 2), q, 'ow ow ow' if i == 0 else None)
kf(23.6, GRAB)
kf(24.0, TURN_AWAY, 'stumble away', yaw=210)
_dir = np.array([np.cos(np.radians(210)), 0, -np.sin(np.radians(210))])
_pos = np.array([X_KICK - 0.08, 0, 0.0])
for i in range(6):
    _pos = _pos + _dir * 0.19
    kf(24.35 + 0.35 * i, LIMP_BAD if i % 2 == 0 else LIMP_GOOD, x=float(_pos[0]), z=float(_pos[2]))
kf(26.6, M(LIMP_GOOD, lumbarside=0, broll=0), x=float(_pos[0] + _dir[0] * 0.12), z=float(_pos[2] + _dir[2] * 0.12))

CAM = (40, 13)

# ---------------------------------------------------------------- tools
def check(fps=15):
    """trace the grounded root height per frame; flag floor sweeps (spikes above the keyframe heights)"""
    from animate import _monotone_tangents, _hermite
    keys = sorted(set(k for _, p in K for k in p if k != 'label'))
    times = np.array([t for t, _ in K]); full = [{k: p.get(k, 0.0) for k in keys} for _, p in K]
    tang = {k: _monotone_tangents(times, np.array([f[k] for f in full])) for k in keys}
    kh = np.array([grounded_height(p) for _, p in K])
    g, ts = [], []
    for i in range(int(times[-1] * fps) + 1):
        t = min(i / fps, times[-1]); j = max(0, min(len(times) - 2, np.searchsorted(times, t, side='right') - 1))
        p = {k: float(_hermite(times, np.array([f[k] for f in full]), tang[k], j, t)) for k in keys}
        g.append(grounded_height(p)); ts.append(t)
    g = np.array(g); ts = np.array(ts); sp = g - np.interp(ts, times, kh)
    print('keyframes:', len(K), ' frames:', len(g), ' X_KICK=%.3f' % X_KICK)
    print('spikes > 8cm:', [f'{t:.2f}(+{v:.2f})' for t, v in zip(ts, sp) if v > 0.08] or 'none')
    print('max frame-to-frame root change: %.3f m' % np.abs(np.diff(g)).max())

def sheet(path, cols=6, W=300, H=190):
    """contact sheet of every keyframe at the animation's fixed framing"""
    from PIL import Image, ImageDraw
    figs = [build({k: v for k, v in p.items() if k not in ('label', 'rooty')}) for _, p in K]
    rows = (len(K) + cols - 1) // cols
    S = Image.new('RGB', (cols * W, rows * H), (255, 255, 255)); d = ImageDraw.Draw(S)
    for i, ((t, p), F) in enumerate(zip(K, figs)):
        if 'rooty' in p: F.root_pos[1] = p['rooty']; F.fk()
        R = render_scene([F], PROPS, cam=CAM, W=W, H=H, ghost_figures=figs, mat=False, tint='continuous')
        im = Image.new('RGBA', R.img.size, (255, 255, 255, 255)); im.alpha_composite(R.img)
        _caption(im, f"{i:02d} t={t:.2f} {p.get('label', '')}", W * 2)
        S.paste(im.convert('RGB'), ((i % cols) * W, (i // cols) * H))
        d.rectangle([(i % cols) * W, (i // cols) * H, (i % cols + 1) * W - 1, (i // cols + 1) * H - 1], outline=(200, 200, 200))
        print(f'{i:02d} t={t:5.2f} lowest={F.lowest():+.3f} rooty={F.root_pos[1]:.3f} {p.get("label", "")}')
    S.save(path); print('wrote', path)

if __name__ == '__main__':
    args = sys.argv[1:]
    workers = int(args[args.index('--workers') + 1]) if '--workers' in args else 1
    if '--check' in args:
        check()
    elif '--sheet' in args:
        sheet(args[args.index('--sheet') + 1])
    else:
        out = next((a for a in args if not a.startswith('--') and a.endswith('.gif')), 'speaker_dance.gif')
        if '--draft' in args:
            print('wrote', sequence(K, build, out, fps=10, cam=CAM, W=440, H=250, props=PROPS, mat=False, hold_last=0.5, workers=workers))
        else:
            print('wrote', sequence(K, build, out, fps=15, cam=CAM, W=880, H=500, props=PROPS, mat=False, hold_last=0.6, workers=workers))
