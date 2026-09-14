# Final, reviewed content. Use verbatim.

TITLE = 'Hip, Groin &amp; Flexibility Routine'
RUNNING_HEADER = 'Hip, groin and flexibility routine'

SUMMARY = ('A one-hour session built around a symptomatic adductor / lower-abdominal junction. '
           'Difficulty comes from time under tension, tempo and precision — not from long levers or end range.')

CONSTRAINTS = [
    ('Provoking loads removed',
     'No long-lever supine leg work (legs in the air, straddle-in-the-air, ankle-weight straight leg raises, hollow holds). No running.'),
    ('Isometrics are the treatment',
     'They belong early in the session, while you are fresh. They should feel **better during**, not worse. If something bites, drop to 50% effort rather than skipping it.'),
    ('Range is on hold',
     'You have range you have not consolidated yet. For the next few weeks, consolidating it will do more for your dancing than another 5 degrees.'),
    ('Order matters',
     'Strength **after** flexibility, or on separate days. Active range before passive depth. Load in the stretched position last.'),
]

SESSION_MAP = [
    (1, 'Warm-up', '8 min', 'raise temperature, moderate range only'),
    (2, 'Isometric block', '14 min', 'the treatment, do it fresh'),
    (3, 'Motor control', '12 min', 'slow, precise, stop when you lose the feel'),
    (4, 'Strength', '16 min', 'posterior chain and anti-rotation'),
    (5, 'Passive flexibility', '10 min', 'not symptomatic — work properly here'),
]

STOP_RULES = ('Back off the session and drop a stage if any of these appear: groin pain that lingers after the session · '
              'pain on coughing or sneezing returning · tingling or numbness in the foot · pain that is worse after warming up rather than better.')

STOP_NOTE = ('This routine is built to work around a symptom, not to diagnose it. Months of loading-specific groin pain still '
             'warrants a sports medicine or dance medicine assessment.')

# exercises: (number, name, dose, cues, flag-or-None)
SECTIONS = [
    dict(num=1, title='Warm-up', duration='8 min', subtitle='moderate range only — nothing near end range', exercises=[
        (1, 'Cat–cow', '10 reps, slow',
         'Alternate arching and sagging the spine. Move segment by segment rather than swinging the whole back at once.', None),
        (2, '90/90 hip switches', '10 per side',
         'Sit with both knees at 90°, rotate both legs to the other side. Keep the torso tall; let the hips do the rotating.', None),
        (3, 'Glute bridge', '15 reps, then 3 × 20s single-leg hold',
         'Drive through the heels, squeeze the glutes at the top. Ribs stay down — do not arch the lower back to gain height.', None),
        (4, 'Deep squat rock-outs', '10 reps',
         'Sit into a deep squat and rock gently side to side, letting each hip open in turn. Heels stay down if they can.', None),
        (5, 'Leg swings', '15 forward/back and 15 side/side, each leg',
         'Relaxed and rhythmic, not forced. Stand tall and keep the pelvis quiet.',
         'Moderate range only — this is not a stretch.'),
        (6, 'Ankle circles + calf raises', '15 each',
         'Circles both directions, then rise onto the toes and lower slowly. Keeps the foot and ankle happy before loading.', None),
    ]),
    dict(num=2, title='Isometric block', duration='14 min', subtitle='the treatment — do this fresh, not at the end',
         intro='Rest 30–45 seconds between sets. Effort around 70% of maximum. These should feel better as you go, not worse. '
               'If one bites, drop the effort to 50% rather than skipping it.',
         exercises=[
        (7, 'Adductor squeeze, knees bent', '5 × 30s at ~70%',
         'Lie on your back, ball or rolled towel between the knees. Squeeze steadily and breathe. No bracing through the jaw or glutes.', None),
        (8, 'Adductor squeeze, legs straight', '4 × 30s at ~70%',
         'Same squeeze with the ball at the ankles. The longer lever changes which part of the adductor group takes the load.', None),
        (9, 'Adductor squeeze, wide position', '3 × 30s at ~70%',
         'Larger ball, knees further apart. Trains the same contraction at a longer muscle length — the position that matters for straddle.', None),
        (10, 'Short-lever Copenhagen hold', '5 × 25s per side',
         'Forearm on the floor, **knee** resting on the bench rather than the foot. Lift the hips so the body makes one line and hold.', None),
        (11, 'Wall psoas hold', '4 × 20s per side',
         'Stand beside a wall, lift the knee **above** 90° and press it into the wall. Stand tall — do not let the pelvis tuck or the torso lean back.', None),
    ]),
    dict(num=3, title='Motor control', duration='12 min', subtitle='slow and precise — stop a drill when you can no longer feel it', exercises=[
        (12, 'Seated pelvic tilts', '20 reps, slow',
         'Sit on a low block, legs straight. Roll the pelvis forward and back with a hand on the low back to check the movement is coming from the pelvis, not the spine.', None),
        (13, 'Wall pike', '3 × 30s',
         'Back against the wall, legs straight. Get the sacrum flat to the wall without the shoulders leaving it. This is your true pike range with no cheating.', None),
        (14, '90/90 lift-offs', '8 per side, 5s holds',
         'From the 90/90 position, lift the front shin about 2 cm off the floor. Small movement, big demand on the deep rotators.', None),
        (15, 'Straddle hover', '5 × 8s',
         'Press the heels into the floor and lift the sit bones fractionally. Teaches the adductors to produce force at length.',
         'Moderate width only while symptoms are settling.'),
        (16, 'Standing développé, bodyweight', '5 per side',
         'Knee above 90°, then extend the leg while keeping the height. Hold 5s. This is the exact transition your développé needs.',
         'Stop if the groin talks.'),
    ]),
    dict(num=4, title='Strength', duration='16 min', subtitle='posterior chain and anti-rotation — nothing long-lever supine', exercises=[
        (17, 'Seated good morning', '3 × 6, slow',
         'Sit on a low block, legs straight, light bar or plate across the shoulders. Hinge forward with a **flat back** and return. Strength at long lengths raises stretch tolerance faster than stretching does.', None),
        (18, 'Jefferson curl', '3 × 5, light (2–5 kg)',
         'Roll down one vertebra at a time off a step, knees straight, then roll back up the same way. Deliberately the opposite of a flat back — controlled loading of spinal flexion.', None),
        (19, 'Pallof press', '3 × 10 per side, 3s holds',
         'Band anchored at chest height to the side. Press straight out and resist the rotation. Anti-rotation core is the direct answer to the supine rotation problem.', None),
        (20, 'Side plank, top leg lifted', '3 × 20s per side',
         'Forearm down, body in one line, lift the top leg and hold. Lateral hip and trunk control without loading the adductor junction.', None),
        (21, 'Short-lever dead bug', '3 × 8 per side',
         'Knees stay bent — heel taps only. Exhale fully, feel the ribs come down, and only move as far as you can hold the low back flat.',
         'Short lever deliberately: long-lever versions are a provoking load right now.'),
        (22, 'Copenhagen eccentric lower', '3 × 5 per side',
         'From the short-lever hold, lower the hips slowly over about 5 seconds, then reset.',
         'Only add this once the isometric version has been quiet for 2+ weeks.'),
    ]),
    dict(num=5, title='Passive flexibility', duration='10 min', subtitle='not symptomatic — this is where you can work properly', exercises=[
        (23, 'Seated fold, PNF', '4 rounds',
         'Fold to your limit. Press the heels down at ~40% for 8s, exhale and sink deeper. Engage the quads to **extend** the knee — do not brace it back into hyperextension. That distinction is the whole thing.', None),
        (24, 'Pancake hold', '3 min at ~70%',
         'Fold from the hips, not the ribs. Long exhales, scan for gripping at the knee, calf and jaw. Low intensity, long duration.', None),
        (25, 'Half-frog', '90s per side',
         'One knee bent out to the side, the other leg straight. Gentler on the knee and the adductor junction than full frog.', None),
        (26, 'Couch stretch', '60s per side',
         'Back shin up against a couch or wall, front foot planted. Tuck the tailbone and squeeze the glute of the back leg, or you will just stress the low back.', None),
    ]),
]

FREQUENCY = [
    ('3× per week', 'Full session as written.'),
    ('Daily (optional)', 'Section 2 alone — 14 minutes, and worth doing.'),
    ('Cardio', 'Cycling, swimming or elliptical. No running for now: every stride pulls across the pubic symphysis with the adductors '
               'decelerating the leg, and it is the load that brought the symptom back.'),
]

ADDING_LOAD = ('Change **one** variable at a time, about two weeks apart. Complete rest works but builds nothing, which is why the '
               'symptom returned last time — isometrics are the middle path.')

LOAD_STEPS = [
    'Short lever → Long lever',
    'Isometric → Eccentric',
    'Moderate range → End range',
    'Unloaded → Loaded in the stretched position',
    'Low-impact cardio → Running, reintroduced gradually',
]

GOOD_SESSION = ('Warm and worked, not sore. The isometrics should feel easier at set five than at set one. Any groin discomfort should '
                'be gone by the next morning. If it is still there, you did too much — drop back a stage rather than pushing through.')

CLOSING = 'Give this three to four weeks with the provoking loads removed before adding anything back.'

CREDITS = ('All 26 figures were rendered for this document from a posed 3D mannequin model (own work). '
           'No third-party artwork, photographs or icon sets are used, so no attribution or share-alike terms apply. '
           'Solid limb = nearer the viewer, pale limb = further away; dashed outline = start position; red arrow = direction of force or movement.')

CREDITS_JSON_NOTE = ('All illustrations are original renders of a procedural 3D mannequin produced for this document; '
                     'no third-party images were used.')
