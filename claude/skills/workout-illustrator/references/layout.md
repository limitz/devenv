# PDF layout and content schema

Stack: reportlab platypus, A4, 16 mm margins, Helvetica throughout (DejaVu Sans only for the
→ and ▲ glyphs). Palette: ink `#1b2a33`, muted `#6b7f8a`, accent `#c2483a`, rule `#d5dee2`,
band `#f2f6f7`.

Pages: 1 cover · one page per section · final "Progression & scheduling" page with an image
credits block at the bottom. Running header on pages 2+ (title left, page number right, hairline).

Exercise row: figure in a 53 mm column (image 50×36 mm), text right: bold name with accent
number, accent dose line, cues at 9.1 pt, optional flag line (▲, italic muted). Hairline below.
Rows are `KeepTogether`; six rows fit one page, so keep cues to ~3 lines.

## content.py

```python
TITLE = 'Hip, Groin &amp; Flexibility Routine'      # reportlab markup: escape & as &amp;
RUNNING_HEADER = 'Hip, groin and flexibility routine'
SUMMARY = '...'                                       # one or two sentences
CONSTRAINTS = [('label', 'text'), ...]                # optional; **bold** allowed
SESSION_MAP = [(1, 'Warm-up', '8 min', 'note'), ...]  # optional
STOP_RULES = '...'                                    # optional, rendered in accent colour
STOP_NOTE = '...'                                     # optional, muted
SECTIONS = [dict(num=1, title='Warm-up', duration='8 min', subtitle='...', intro=None,
                 exercises=[(1, 'Cat–cow', '10 reps, slow', 'cues ...', None),   # (n, name, dose, cues, flag|None)
                            ...]), ...]
FREQUENCY = [('3× per week', 'Full session as written.'), ...]   # optional
ADDING_LOAD = '...'; LOAD_STEPS = ['Short lever → Long lever', ...]   # optional
GOOD_SESSION = '...'; CLOSING = '...'                              # optional
CREDITS = 'All figures rendered for this document ...'            # optional block text
CREDITS_JSON_NOTE = '...'; THIRD_PARTY_IMAGES = []                # written to credits.json
```

Exercise numbers must match the figure filenames `figures/NN.png` produced by `compose.py`.
If third-party art is ever used, list each file (filename, author, licence, source URL) in
`THIRD_PARTY_IMAGES` and in `CREDITS`; CC BY-NC and unlicensed images are not acceptable.
