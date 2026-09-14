"""Lyrical phrase with floorwork: hip sways with an arm sweep, body wave, spiral down through a
kneeling lunge into a side-sit, floor developpe, lie back with the leg up, leg sweep, roll to the
side, push up to the side-sit, kneel, rise to a final pose.
usage: python3 lyrical.py [out.gif]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import numpy as np
from mannequin import *
from animate import sequence, param_pose

def build(p):
    F = Figure(param_pose(p), root_pos=(p.get('x', 0.0), 0.96, p.get('z', 0.0)))
    F.ground()
    return F

def arm(side, flex=0, abd=0, elbow=0, rot=0):
    return {'uflex' + side: flex, 'uabd' + side: abd, 'elbow' + side: elbow, 'urot' + side: rot}
def leg(side, flex=0, abd=0, knee=0, foot=0, rot=0):
    return {'tflex' + side: flex, 'tabd' + side: abd, 'knee' + side: knee, 'foot' + side: foot, 'trot' + side: rot}

# --- standing styling ---------------------------------------------------------------------------
swayL = {**leg('L', flex=4, abd=8, knee=6), **leg('R', flex=8, abd=10, knee=22, foot=10), 'roll': 7, 'lumbarside': -8,
         'thoraxside': -3, 'neckside': 9, **arm('L', flex=14, abd=24, elbow=30), **arm('R', flex=150, abd=28, elbow=28)}
swayR = {**leg('R', flex=4, abd=8, knee=6), **leg('L', flex=8, abd=10, knee=22, foot=10), 'roll': -7, 'lumbarside': 8,
         'thoraxside': 3, 'neckside': -9, **arm('R', flex=14, abd=24, elbow=30), **arm('L', flex=150, abd=28, elbow=28)}
base_legs = {**leg('L', flex=6, abd=9, knee=12), **leg('R', flex=6, abd=9, knee=12)}
wave1 = {**base_legs, 'lumbar': 22, 'thorax': -6, 'neck': 14, **arm('L', flex=10, abd=40, elbow=20), **arm('R', flex=10, abd=40, elbow=20)}
wave2 = {**base_legs, 'lumbar': -14, 'thorax': 20, 'neck': 4, **arm('L', flex=30, abd=60, elbow=25), **arm('R', flex=30, abd=60, elbow=25)}
wave3 = {**base_legs, 'lumbar': 2, 'thorax': -18, 'neck': -14, **arm('L', flex=40, abd=92, elbow=10), **arm('R', flex=40, abd=92, elbow=10)}
spiral = {**leg('L', flex=40, abd=18, knee=80, rot=35), **leg('R', flex=40, abd=18, knee=80, rot=35), 'lumbartwist': 28,
          'thoraxtwist': 14, 'lumbar': 12, **arm('L', flex=70, abd=-10, elbow=60), **arm('R', flex=20, abd=70, elbow=20)}
# --- kneeling lunge: right knee down (shin flat behind), left foot forward flat ------------------
kneel = {**leg('R', flex=0, abd=6, knee=92, foot=40), **leg('L', flex=88, abd=8, knee=90), 'lumbar': 6,
         **arm('L', flex=60, abd=10, elbow=40), **arm('R', flex=-10, abd=80, elbow=10), 'neckside': 6}
# --- side-sit (legs folded to the dancer's left), right hand on the floor -------------------------
sidesit = {**leg('R', flex=90, knee=90, rot=90, foot=25), **leg('L', abd=90, knee=90, foot=25), 'lumbarside': 6,
           **arm('R', flex=-24, abd=48, elbow=12), **arm('L', flex=150, abd=22, elbow=26), 'neckside': -8}
# --- floor developpe: front (right) leg extends straight along the floor ---------------------------
floordev = {**leg('R', flex=92, knee=0, rot=30, foot=45), **leg('L', abd=90, knee=90, foot=25), 'lumbar': -12,
            **arm('R', flex=-40, abd=30, elbow=10), **arm('L', flex=-40, abd=30, elbow=10)}
# --- lie back, right leg to the ceiling, left knee bent foot flat --------------------------------
lieback = {'pitch': 90, **leg('R', flex=96, foot=45), **leg('L', flex=62, knee=122, foot=-6),
           **arm('R', flex=165, abd=18, elbow=8), **arm('L', flex=165, abd=18, elbow=8), 'neck': -6}
sweep = {'pitch': 90, **leg('R', flex=60, abd=72, foot=45), **leg('L', flex=62, knee=122, foot=-6),
         **arm('R', flex=20, abd=90, elbow=6), **arm('L', flex=20, abd=90, elbow=6), 'lumbarside': 6}
# --- roll onto the left side, legs folded, top arm reaching -------------------------------------
sidelie = {'pitch': 90, 'yaw': 95, **leg('R', flex=70, knee=95, foot=35), **leg('L', flex=50, knee=100, foot=35),
           **arm('L', flex=100, abd=10, elbow=90), **arm('R', flex=120, abd=-10, elbow=10), 'lumbar': 10, 'neck': 8}
# --- push up to the side-sit, then kneel, then rise ------------------------------------------------
pushup = {'pitch': 30, 'yaw': 30, **leg('R', flex=90, knee=90, rot=80, foot=25), **leg('L', abd=80, knee=95, foot=25),
          **arm('L', flex=-20, abd=60, elbow=10), **arm('R', flex=110, abd=20, elbow=20), 'lumbar': 14, 'lumbartwist': -10}
rise = {**leg('L', flex=28, abd=10, knee=40), **leg('R', flex=8, abd=10, knee=14, foot=20), 'lumbar': 8,
        **arm('L', flex=120, abd=30, elbow=25), **arm('R', flex=120, abd=30, elbow=25), 'x': 0.2}
final = {**swayL, 'x': 0.2, **arm('L', flex=160, abd=22, elbow=24), **arm('R', flex=20, abd=45, elbow=30), 'neckside': 10}

K = [(0.0, swayL), (0.9, swayR), (1.7, wave1), (2.1, wave2), (2.5, wave3), (3.1, spiral), (3.8, kneel),
     (4.6, sidesit), (5.4, floordev), (6.2, lieback), (6.9, sweep), (7.7, sidelie), (8.5, pushup), (9.1, sidesit),
     (9.8, kneel), (10.4, rise), (11.0, final), (11.5, final)]

out = sys.argv[1] if len(sys.argv) > 1 else 'lyrical.gif'
mat = box((-0.95, -0.012, -0.85), (1.25, 0.0, 0.85), color='mat', fit=False, group='mat')
print('wrote', sequence(K, build, out, fps=12, cam=(42, 22), W=800, H=580, props=[mat], mat=False, hold_last=0.3))
