# Posing reference

## Frames and conventions

- World: figure faces **+X**, up is **+Y**, the figure's **left is +Z**. Floor is y = 0.
- Standing rest pose: `Figure({})` with root (pelvis centre) at (0, 0.96, 0); height 1.72 m.
- Every bone takes a list of `(axis, degrees)` rotations applied **in list order** in the parent
  frame. Helpers return such tuples:

| helper | meaning | sign |
| --- | --- | --- |
| `flex(d)` | hip/shoulder flexion (limb swings forward) | + forward; use `flex(-d)` for extension |
| `kflex(d)` | knee flexion (foot swings back) | + |
| `eflex(d)` | elbow flexion (hand swings forward) | + |
| `tflex(d)` | trunk/neck forward bend (lumbar, thorax, neck) | + forward; `tflex(-d)` = extension |
| `abd(side, d)` | abduction away from the midline | side 'L' or 'R' |
| `ext_rot(side, d)` | external (lateral) rotation about the limb axis | |
| `pitch(d)` | root rotation about Z | `pitch(-90)` = prone/quadruped (head to +X), `pitch(90)` = supine (head to −X) |

Bones: `root, lumbar, thorax, neck, head, uarmL/R, farmL/R, handL/R, thighL/R, shinL/R, footL/R`.
Order within a limb list: axial rotation first, then abduction, then flexion, e.g.
`'thighL': [ext_rot('L', 90), flex(90)]` (90/90 front leg), `'thighR': [abd('R', 90)]` (90/90 back leg).

Side-lying, body facing the viewer, head to the left: `'root': [('z', 90), ('x', 90)]`
(lying on the left side; the right leg is the top leg; pass `near='R'` to `Figure`).

## Building a scene

```python
from mannequin import *
from poselib import A, off      # A(p0, p1, rad=0, style='->'|'<->', size=1.0); off(p, dx, dy, dz)

def my_pose():
    pose = {'root': [pitch(90)], 'thighL': [flex(60)], 'shinL': [kflex(120)], ...}
    F = Figure(pose, root_pos=(0, 0.11, 0)); F.ground()     # ground() sets lowest surface to y=0
    k = F.J('kneeL')                                          # joints: pelvis chest neckbase head headtop
    arrows = [A(off(k, 0, 0.3, 0), off(k, 0, 0.1, 0))]        #   hipX kneeX ankleX toeX heelX shoulderX
    props = [ball((0.3, 0.2, 0), 0.09), box((x0,0,z0), (x1,h,z1)), rod(a, b, r, color='band')]
    return dict(figures=[F], ghosts=[], props=props, cam='high', arrows=arrows, label=None)
```

Scene dict keys: `figures` (list), `ghosts` (start-position figures, drawn as dashed outline),
`props`, `cam` (name from `CAMS` or `(az, el)`), `arrows`, `label` (viewpoint text, bottom-left),
optional `fit_pts` (world points that must be in frame), `mat` (default True).

Arrow kinds: `A(...)` straight or `rad`-curved; circular:
`dict(kind='circ', c=point, r=metres, a0=200, a1=-120, size=0.9)`.

## IK and solving

```python
ik, phi_f = arm_ik(F, 'L', target_xyz)   # returns pose entries for uarmL/farmL (sagittal plane)
pose.update(ik); pose['handL'] = [('z', 90 - phi_f)]   # hand flat on the floor
ik, _ = leg_ik(F, 'R', ankle_target)
F = Figure(pose, root_pos=...); F.ground()             # rebuild, THEN ground
```
For one unknown angle (knee must land on a bench, foot must touch the floor) bisect on it; verify
the monotonic direction with two probes before trusting the result (see `copenhagen` in poselib).

## Cameras (`CAMS`)

`side` (25, 14) · `sideb` (−25, 14) · `high` (35, 38) · `high2` (50, 45) · `high45` (45, 36)
· `front` (62, 18) · `frontface` (0, 14) · `top` (20, 62).
Azimuth 0 = viewer on the figure's left; 90 = in front. Near/far limb shading is picked from hip
depth automatically; override with `Figure(..., near='R')`.

## Colours and rendering

Figure torso `#93a8b3`, near limb `#6b7f8a`, far limb `#c6d2d8`, props `#ddd8cf`, ball `#b9a48c`,
band `#8a7a6a`, mat `#eaf0f2`, ink outline `#1b2a33`, arrows `#c2483a`. Output 1020×740 px
transparent PNG (51×37 mm at 20 px/mm), 2× supersampled, ~2–4 s per tile.

## Recipes (all in poselib)

quadruped `cat_cow` · seated on floor `seated_base`, `wall_pike`, `seated_fold` · seated on block
`pelvic_tilts`, `seated_good_morning` · supine `glute_bridge`, `adductor`, `dead_bug` · prone
`half_frog` · side-lying `copenhagen`, `side_plank` · standing `leg_swings`, `developpe`, `pallof`,
`wall_psoas`, `ankle_calf` (two figures in one tile) · squat `deep_squat` · kneeling `couch` ·
straddle `straddle_hover`, `pancake` · 90/90 `ninety_ninety(lift=False|True)` · on a box `jefferson`.

## Pitfalls seen

- Ghost drift: building the ghost with its own `ground()` shifts it; share the root and IK the
  hands/knees to fixed targets.
- Top-down (el ≥ 60) views of seated poses were unreadable; `high2` at 45° elevation reads well.
- Walls make the auto-fit tiny; exclude them (`fit=False`) and add a `fit_pts` point at head height.
- Arrow endpoints are added to the fit automatically, so a long arc can shrink the figure; keep
  arrows near the body.
