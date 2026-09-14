---
name: workout-illustrator
description: "Produce an illustrated, print-ready A4 exercise routine PDF where every exercise has a clear, consistent figure. Use whenever the user asks for a workout / training / mobility / stretching / rehab routine with pictures, an exercise sheet or programme PDF, or figures of a body position (yoga pose, stretch, dance exercise, gym movement). Renders a posed 3D capsule mannequin (own artwork, no licensing) with red movement arrows and dashed start-position ghosts, then lays out the PDF with reportlab. Also use to add or fix a single exercise figure in an existing routine."
---

# Workout illustrator

Renders exercise figures from a posed capsule mannequin (numpy ray-caster, no Blender, no network)
and builds an A4 routine PDF around them. Every figure comes from the same model, camera set and
palette, so a 26-exercise document reads as one family. All artwork is generated, so there is
nothing to credit or license.

Engine lives next to this file: `engine/mannequin.py` (skeleton, FK, IK, renderer),
`engine/poselib.py` (26 ready scenes + helpers), `engine/compose.py` (figures + contact sheet),
`engine/build_pdf.py` (layout), `engine/animate.py` (GIF/MP4 loops). Worked example: `examples/hip-groin-flexibility/`.

Requirements: python3 with numpy, scipy, matplotlib, Pillow, reportlab; `pdftoppm` for checking pages.

## Workflow

1. **Write `content.py`** for the routine (schema in `references/layout.md`; copy the example and
   edit). Keep the user's text verbatim — clinical framing, flags and doses are not yours to soften.
2. **Write `scenes.py`**: `SCENES = [(number, name, fn), ...]`, one entry per exercise, numbers
   matching `content.py`. Reuse functions from `poselib` where the exercise already exists
   (`from poselib import glute_bridge, adductor, ...`); write new ones following
   `references/posing.md`. Look at the closest existing pose first and copy its structure.
3. **Render and look**:
   `python3 engine/compose.py --scenes scenes.py --out figures` then open `figures/sheet.png`.
   Check every tile: pose anatomically right, head direction clear (the nose bump), ground contact
   real (printed `lowest` should be 0.000 for floor poses), near limb dark / far limb pale,
   arrow visible and not foreshortened, nothing cut off. Re-render single tiles with `--only N`.
   Iterate until the sheet is clean; do not ship a tile you have not looked at.
4. **Build the PDF**:
   `python3 engine/build_pdf.py --content content.py --figures figures --out routine.pdf`
   then `pdftoppm -r 60 -png routine.pdf pages/p` and look at the pages. Each section must fit
   one page (rows are `KeepTogether`; if a section spills, shorten cues or drop the image cap to
   35 mm in `build_pdf.py`). `credits.json` is written next to the PDF.
5. Deliver the PDF (SendUserFile) and say which poses were reused vs new.
6. **Animation on request**: `engine/animate.py` tweens a `build(s)` function between two poses
   (cosine ping-pong loop, fixed framing) into a GIF plus MP4; see
   `examples/hip-groin-flexibility/animate_catcow.py`. Keep the root fixed and pin hands/feet
   with IK inside `build`, so only the moving segments move. ~1.5 s per frame at 680×493.
   For multi-step choreography use `animate.sequence(keyframes, build, path)`: keyframes are
   `(time_s, params)` dicts of plain numbers, interpolated with smoothstep and fed to your
   `build(params)`; `animate.param_pose(params)` turns a flat dict of joint numbers into a pose.
   Keyframes take an optional ease ('smooth', 'linear', 'in', 'out') for the segment they start.
   See `examples/fun/karate.py` (punches, flying kick, bow; airborne frames set the root height
   explicitly) and `examples/fun/ballet.py` (fifth, pas de bourrée, pirouette with linear spin,
   révérence; turnout via `trotX`, demi-pointe via `footX`, fixed `near='L'` so shading does not
   flip while turning).

## Rules of thumb that cost time to learn

- Camera classes are fixed: `side` for most things, `sideb` when a wall is in front,
  `high` for supine/prone, `high2` (labelled "viewed from above, front-left") for seated 90/90
  and straddle, `frontface` for side-lying bodies rolled to face the viewer, `(az, el)` tuple for
  a one-off. Do not invent a new camera per exercise.
- A forward-pointing arrow vanishes in a front view (it points at the camera). Choose the camera
  so the movement direction lies across the image.
- Solve arm/leg targets with `arm_ik` / `leg_ik`, then call `ground()` **after** IK, never before.
- Props that drive the framing (bench, block) use `fit=True`; walls and barres use `fit=False`
  plus a `fit_pts` entry so the frame stops just above the head.
- Ghost = start position, rendered from the same root so hands/knees stay put; only the moving
  parts differ.
- When a solve (bisection) is needed, check the monotonic direction first — a wrong sign silently
  puts a knee on the floor.
- Multi-figure tiles (two mini scenes side by side) are fine for paired drills.
