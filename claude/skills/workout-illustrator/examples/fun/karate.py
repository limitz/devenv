"""Just for fun: guard, two punches, a flying front kick, landing, and a bow.
usage: python3 karate.py [out.gif]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import numpy as np
from mannequin import *
from animate import sequence

from animate import param_pose as pose_from

def build(p):
    F = Figure(pose_from(p), root_pos=(p.get('x', 0.0), 0.96, 0.0))
    F.ground()                                         # sequence() lifts airborne frames via their 'rooty'
    return F

def rooty(p):
    """root height of the grounded version of p (used to place airborne keyframes)"""
    F = Figure(pose_from(p), root_pos=(0, 0.96, 0)); F.ground(); return F.root_pos[1]

# --- keyframes ---------------------------------------------------------------------------------
GUARD = dict(tflexL=18, kneeL=36, tabdL=12, tflexR=18, kneeR=36, tabdR=12, footL=-2, footR=-2,
             uflexL=40, uabdL=12, elbowL=115, uflexR=30, uabdR=14, elbowR=120, lumbar=6, yaw=10)   # left shoulder forward
def punch(side):
    other = 'R' if side == 'L' else 'L'
    q = dict(GUARD)
    q.update({'uflex' + side: 92, 'uabd' + side: 2, 'elbow' + side: 4,          # striking arm straight out
              'uflex' + other: -22, 'uabd' + other: 8, 'elbow' + other: 118,   # other fist chambered at the hip
              'yaw': 24 if side == 'L' else -24, 'lumbar': 10})   # punching shoulder comes forward
    return q
CROUCH = dict(GUARD, tflexL=34, kneeL=62, tflexR=34, kneeR=62, lumbar=14)
def flight(x, up, kick):
    q = dict(x=x, air=1, pitch=14, lumbar=-4,
             tflexR=kick, kneeR=6, footR=-8, tabdR=4,                          # kicking leg
             tflexL=70, kneeL=118, footL=25, tabdL=10,                        # tucked leg
             uflexL=80, uabdL=8, elbowL=70, uflexR=-30, uabdR=20, elbowR=100)
    q['rooty'] = rooty(CROUCH) + up
    return q
LAND = dict(GUARD, x=0.55, tflexL=30, kneeL=55, tflexR=30, kneeR=55, lumbar=16, uflexL=60, elbowL=90, uflexR=50, elbowR=95)
TALL = dict(x=0.55, uabdL=6, uabdR=6, elbowL=6, elbowR=6, footL=0, footR=0)
BOW = dict(TALL, lumbar=38, thorax=12, neck=6, uflexL=4, uflexR=4)

KEYS = [(0.0, {**GUARD, 'label': 'guard'}), (0.5, GUARD), (0.7, {**punch('L'), 'label': 'left punch'}), (0.9, punch('L')),
        (1.1, {**punch('R'), 'label': 'right punch'}), (1.3, punch('R')),
        (1.65, {**CROUCH, 'label': 'flying front kick'}), (1.95, flight(0.18, 0.30, 70)), (2.15, flight(0.32, 0.42, 100)), (2.32, flight(0.45, 0.30, 92)),
        (2.55, {**LAND, 'label': 'landing'}), (3.05, {**TALL, 'label': 'bow'}), (3.5, BOW), (4.2, BOW), (4.7, TALL)]

out = sys.argv[1] if len(sys.argv) > 1 else 'karate.gif'
mat = box((-0.75, -0.012, -0.55), (1.35, 0.0, 0.55), color='mat', fit=False, group='mat')
print('wrote', sequence(KEYS, build, out, fps=12, cam=(38, 12), props=[mat], mat=False, hold_last=0.6))
