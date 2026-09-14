"""Ballet phrase: fifth position, demi-plie, pas de bourree dessous (travelling to the dancer's left),
preparation in fourth, double pirouette en dehors in retire, finish in fourth, reverence.
usage: python3 ballet.py [out.gif]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import numpy as np
from mannequin import *
from animate import sequence, param_pose

TURNOUT = 55
def build(p):
    F = Figure(param_pose(p), root_pos=(p.get('x', 0.0), 0.96, p.get('z', 0.0)))
    F.ground()                     # sequence() smooths the height afterwards
    return F

def legs(**kw):
    q = dict(trotL=TURNOUT, trotR=TURNOUT); q.update(kw); return q

# arm positions (rounded): bras bas, first, second, fifth en haut
BRAS_BAS = dict(uabdL=22, uabdR=22, uflexL=14, uflexR=14, elbowL=24, elbowR=24)
FIRST = dict(uabdL=16, uabdR=16, uflexL=52, uflexR=52, elbowL=62, elbowR=62)
SECOND = dict(uabdL=82, uabdR=82, uflexL=12, uflexR=12, elbowL=18, elbowR=18)
def arms(a, **kw): q = dict(a); q.update(kw); return q

# --- keyframes ---------------------------------------------------------------------------------
fifth = legs(tflexR=4, tabdR=-14, tflexL=-4, tabdL=-4)                       # right foot front, crossed
K = []
K.append((0.0, {**fifth, **BRAS_BAS, 'label': 'fifth position, bras bas'}))
K.append((0.6, {**fifth, **BRAS_BAS}))
K.append((0.7, {**fifth, **BRAS_BAS, 'label': 'demi-plie, arms to first'}))
K.append((1.2, {**fifth, 'kneeL': 48, 'kneeR': 48, 'tflexL': 20, 'tflexR': 28, **FIRST}))       # demi-plie, arms first
# pas de bourree dessous: back (right, demi-pointe) - side (left, demi-pointe) - front (right, plie)
K.append((1.6, {**legs(tflexR=-16, tabdR=2, footR=48, tflexL=2, tabdL=-2, footL=48), 'x': -0.06, **FIRST, 'label': 'pas de bourree dessous'}))
K.append((1.95, {**legs(tflexL=0, tabdL=24, footL=48, tflexR=-4, tabdR=2, footR=48), 'x': -0.02, 'z': 0.22, **SECOND}))
K.append((2.3, {**legs(tflexR=22, tabdR=-7, kneeR=42, tflexL=14, tabdL=2, kneeL=42), 'z': 0.42, **FIRST}))
# preparation in fourth: right foot back, left front in plie; right arm first, left arm second
prep = {**legs(tflexR=-26, tabdR=-4, tflexL=24, kneeL=46, tabdL=-2), 'z': 0.42,
        **arms(FIRST, uabdL=82, uflexL=12, elbowL=18)}
K.append((2.8, {**prep, 'label': 'preparation in fourth'}))
# releve + retire, arms close to first, then the double turn
retire = {**legs(tflexL=0, footL=50, trotR=62, tabdR=42, tflexR=58, kneeR=126, footR=45), 'z': 0.42, **FIRST}
K.append((3.15, {**retire, 'yaw': 0, 'label': 'double pirouette en dehors'}, 'in'))
K.append((3.4, {**retire, 'yaw': 150}, 'linear'))
K.append((3.95, {**retire, 'yaw': 600}, 'out'))
K.append((4.25, {**retire, 'yaw': 720}))
# finish in fourth plie, arms open to second
finish = {**legs(tflexR=-26, tabdR=-4, kneeR=30, tflexL=24, kneeL=48, tabdL=-2), 'z': 0.42, 'yaw': 720, **SECOND}
K.append((4.6, {**finish, 'label': 'finish in fourth'}))
K.append((5.1, finish))
# reverence: right leg crosses behind, plie, slight bow, arms lower
rev = {**legs(tflexR=-24, tabdR=-24, kneeR=30, footR=42, tflexL=26, kneeL=50, tabdL=6), 'z': 0.42, 'yaw': 720,
       'lumbar': 22, 'thorax': 6, 'neck': 14, **arms(BRAS_BAS, uabdL=40, uabdR=40)}
# back toe on the floor: solve the back knee so the pointed toe and the front sole share the lowest point
def _gap(kr):
    G = Figure(param_pose({**rev, 'kneeR': kr}), root_pos=(0, 0.96, 0))
    R, pw = G.T['footR']; toe = (pw + R @ np.array([FOOT_TOE, FOOT_DROP, 0]))[1] - FOOT_R
    Rl, pl = G.T['footL']; sole = min((pl + Rl @ np.array([FOOT_TOE, FOOT_DROP, 0]))[1], (pl + Rl @ np.array([FOOT_HEEL, FOOT_DROP, 0]))[1]) - FOOT_R
    return toe - sole
lo, hi = 0.0, 80.0                    # more knee bend lifts the toe (gap increases with kneeR)
for _ in range(40):
    mid = (lo + hi) / 2
    if _gap(mid) < 0: lo = mid
    else: hi = mid
rev['kneeR'] = (lo + hi) / 2
K.append((5.7, {**rev, 'label': 'reverence'}))
K.append((6.4, rev))
K.append((7.0, {**fifth, 'z': 0.42, 'yaw': 720, **BRAS_BAS}))

out = sys.argv[1] if len(sys.argv) > 1 else 'ballet.gif'
mat = box((-0.7, -0.012, -0.55), (0.8, 0.0, 1.05), color='mat', fit=False, group='mat')
print('wrote', sequence(K, build, out, fps=12, cam=(55, 10), props=[mat], mat=False, hold_last=0.5))
