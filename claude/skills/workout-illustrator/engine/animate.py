"""Tween a Figure between poses and write a looping GIF (and MP4 when ffmpeg is present).

    from animate import tween_loop
    tween_loop(build, 'cat-cow.gif', N=36, fps=12, cam='side')

`build(s)` returns a Figure for phase s in [0, 1]; the loop runs s: 0 -> 1 -> 0 with a cosine ease,
so build(0) is the start position and build(1) the end position. Framing is fixed from the two
extremes so the figure does not jump between frames. Keep the root fixed inside build() and use
arm_ik / leg_ik to pin hands and feet, exactly as for a still.
"""
import os, io, subprocess, shutil
import numpy as np
from PIL import Image
from mannequin import render_scene

def tween_loop(build, path, N=36, fps=12, cam='side', W=680, H=493, props=(), pingpong=True, colors=128, tint='continuous'):
    ext = [build(0.0), build(1.0)]
    frames = []
    for i in range(N):
        t = i / N
        s = 0.5 - 0.5 * np.cos(2 * np.pi * t) if pingpong else t
        R = render_scene([build(s)], props, cam=cam, W=W, H=H, ghost_figures=ext, tint=tint)
        im = Image.new('RGBA', R.img.size, (255, 255, 255, 255)); im.alpha_composite(R.img)
        frames.append(im.convert('P', palette=Image.ADAPTIVE, colors=colors))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=gif_durations(len(frames), fps), loop=0, optimize=True)
    write_mp4(os.path.splitext(path)[0] + '.mp4', [_png(f) for f in frames], fps)
    return path


# ---------------------------------------------------------------- encoders
H264_ENCODERS = (['-c:v', 'libx264', '-crf', '20', '-preset', 'slow'],
                 ['-c:v', 'h264_nvenc', '-preset', 'p5', '-rc', 'vbr', '-cq', '23', '-b:v', '0'],
                 ['-c:v', 'libopenh264', '-b:v', '1500k'],
                 ['-c:v', 'h264_v4l2m2m', '-b:v', '1500k'],
                 ['-c:v', 'mpeg4', '-q:v', '3'])

def write_mp4(path, png_frames, fps):
    """H.264 MP4 (yuv420p, faststart) from a list of PNG-encoded frames at exactly fps; first encoder
    that works wins (libx264, NVENC, openh264, v4l2, then plain mpeg4 as a last resort). Returns the
    encoder name or None when ffmpeg is missing."""
    if not shutil.which('ffmpeg'):
        return None
    data = b''.join(png_frames)
    for enc in H264_ENCODERS:
        r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(fps), '-i', '-',
                            '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p', *enc, '-movflags', '+faststart', path],
                           input=data, stderr=subprocess.DEVNULL)
        if r.returncode == 0:
            return enc[1]
    return None

def gif_durations(n, fps):
    """per-frame GIF durations (ms) on the 10 ms grid whose running total tracks n/fps exactly"""
    out, acc = [], 0.0
    for i in range(1, n + 1):
        d = int(round(i * 1000 / fps / 10)) * 10 - int(round(acc))
        out.append(max(10, d)); acc += out[-1]
    return out

def _png(im):
    buf = io.BytesIO(); im.convert('RGB').save(buf, 'PNG'); return buf.getvalue()

# ---------------------------------------------------------------- parametric pose template
def param_pose(p):
    """Pose dict from a flat dict of numbers (missing keys = 0). Keys:
    yaw pitch roll (root; for a lying body yaw rolls it about its long axis) ·
    lumbar thorax neck (forward bend), lumbarside thoraxside neckside (lateral bend, + = to the left),
    lumbartwist thoraxtwist neckyaw (twist) ·
    per side X in L/R: uflexX uabdX urotX elbowX handX (arm) · tflexX tabdX trotX kneeX footX (leg;
    trotX = external rotation, footX = plantarflexion, negative = toes up)."""
    g = lambda k: p.get(k, 0.0)
    sgn = {'L': 1, 'R': -1}
    pose = {'root': [('y', g('yaw')), ('x', g('roll')), ('z', g('pitch'))],
            'lumbar': [('y', g('lumbartwist')), ('x', g('lumbarside')), ('z', -g('lumbar'))],
            'thorax': [('y', g('thoraxtwist')), ('x', g('thoraxside')), ('z', -g('thorax'))],
            'neck': [('y', g('neckyaw')), ('x', g('neckside')), ('z', -g('neck'))]}
    for s_ in 'LR':
        pose['uarm' + s_] = [('y', -sgn[s_] * g('urot' + s_)), ('x', -sgn[s_] * g('uabd' + s_)), ('z', g('uflex' + s_))]
        pose['farm' + s_] = [('z', g('elbow' + s_))]
        pose['hand' + s_] = [('z', g('hand' + s_))]
        pose['thigh' + s_] = [('y', -sgn[s_] * g('trot' + s_)), ('x', -sgn[s_] * g('tabd' + s_)), ('z', g('tflex' + s_))]
        pose['shin' + s_] = [('z', -g('knee' + s_))]
        pose['foot' + s_] = [('z', -g('foot' + s_))]
    return pose

# ---------------------------------------------------------------- captions
def _font(size):
    from PIL import ImageFont
    try:
        import matplotlib
        return ImageFont.truetype(os.path.join(os.path.dirname(matplotlib.__file__), 'mpl-data', 'fonts', 'ttf', 'DejaVuSans.ttf'), size)
    except Exception:
        return ImageFont.load_default()

def _caption(im, text, W):
    """small muted caption, top-left, with a white halo for legibility"""
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    size = max(12, int(W * 0.024)); f = _font(size)
    x, y = int(W * 0.03), int(W * 0.025)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text((x + dx, y + dy), text, font=f, fill=(255, 255, 255, 255))
    d.text((x, y), text, font=f, fill=(107, 127, 138, 255))

# ---------------------------------------------------------------- keyframe sequences
def _smooth(t):
    return t * t * (3 - 2 * t)

EASE = {'smooth': _smooth, 'linear': lambda t: t, 'in': lambda t: t * t, 'out': lambda t: 1 - (1 - t) ** 2}

def _monotone_tangents(t, v):
    """Fritsch-Carlson tangents: C1 cubic through the knots, no overshoot, flat through holds."""
    n = len(t)
    if n < 2:
        return np.zeros(n)
    d = np.array([(v[i + 1] - v[i]) / (t[i + 1] - t[i]) if t[i + 1] > t[i] else 0.0 for i in range(n - 1)])
    m = np.zeros(n)
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        m[i] = 0.0 if d[i - 1] * d[i] <= 0 else (d[i - 1] + d[i]) / 2
    for i in range(n - 1):
        if d[i] == 0:
            m[i] = m[i + 1] = 0.0
        else:
            a, b = m[i] / d[i], m[i + 1] / d[i]
            r = a * a + b * b
            if r > 9:
                tau = 3 / np.sqrt(r); m[i] = tau * a * d[i]; m[i + 1] = tau * b * d[i]
    return m

def _hermite(t, v, m, j, x):
    h = t[j + 1] - t[j]
    if h <= 0:
        return v[j + 1]
    u = (x - t[j]) / h
    h00 = 2 * u**3 - 3 * u**2 + 1; h10 = u**3 - 2 * u**2 + u; h01 = -2 * u**3 + 3 * u**2; h11 = u**3 - u**2
    return h00 * v[j] + h10 * h * m[j] + h01 * v[j + 1] + h11 * h * m[j + 1]

_JOB = None   # frame job shared with forked render workers (set by sequence)

def _render_frame(i):
    J = _JOB; F = J['figs'][i]
    R = render_scene([F], J['props'], cam=J['cam'], W=J['W'], H=J['H'], ghost_figures=J['fit_figs'], mat=J['mat'], tint=J['tint'])
    im = Image.new('RGBA', R.img.size, (255, 255, 255, 255)); im.alpha_composite(R.img)
    if J['caps'][i]:
        _caption(im, J['caps'][i], J['W'])
    buf = io.BytesIO(); im.convert('RGB').save(buf, 'PNG'); return buf.getvalue()

def sequence(keyframes, build, path, fps=12, cam='side', W=680, H=493, props=(), mat=None, colors=128, hold_last=0.0,
             tint='continuous', flow=True, smooth_ground=True, workers=1):
    """keyframes: list of (time_s, params_dict[, ease]). build(params) -> Figure.
    flow=True (default): every numeric param follows a monotone cubic spline through all keyframes, so
      motion flows through a keyframe instead of stopping at it (holds stay flat, no overshoot).
      flow=False: per-segment easing with the optional third element 'smooth'|'linear'|'in'|'out'.
    Root height: build() grounds every frame; sequence() then replaces the per-frame height by a smooth
      envelope of it (max filter over +-0.25 s, then a moving average), so a limb that briefly dips below
      the floor between keyframes lifts the body gently instead of bouncing it, and nothing ever pokes
      out under the mat. A keyframe may carry 'rooty' (explicit height for airborne poses); the final
      height is max(envelope, interpolated rooty). Big sweeps through the floor still need a better
      intermediate keyframe: check the printed spikes.
    A keyframe params dict may carry 'label': text shown at the top of the frames from that keyframe on.
    Framing is fixed from all keyframe figures. Writes a GIF (+ MP4 when ffmpeg can encode).
    workers > 1 renders the frames in parallel processes (fork); frames are independent, so this is a
    near-linear speed-up on a multi-core box."""
    keyframes = [(kf[0], dict(kf[1]), kf[2] if len(kf) > 2 else 'smooth') for kf in keyframes]
    labels = [p.pop('label', None) for _, p, _ in keyframes]
    keys = sorted(set(k for _, p, _ in keyframes for k in p))
    times = [t for t, _, _ in keyframes]
    eases = [e for _, _, e in keyframes]
    full = [{k: p.get(k, 0.0) for k in keys} for _, p, _ in keyframes]
    fit_figs = [build(p) for p in full]
    T = times[-1] + hold_last
    n = int(round(T * fps)) + 1
    tarr = np.array(times, float)
    tang = {k: _monotone_tangents(tarr, np.array([f[k] for f in full], float)) for k in keys} if flow else None
    # pass 1: interpolate params, build grounded figures, read the pose-derived root height g[i]
    params, figs, g, air = [], [], [], []
    for i in range(n):
        t = min(i / fps, times[-1])
        j = max(0, min(len(times) - 2, np.searchsorted(times, t, side='right') - 1))
        if flow:
            p = {k: float(_hermite(tarr, np.array([f[k] for f in full], float), tang[k], j, t)) for k in keys}
        else:
            t0, t1 = times[j], times[j + 1]
            u = EASE[eases[j]]((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
            p = {k: full[j][k] + (full[j + 1][k] - full[j][k]) * u for k in keys}
        air.append(p.pop('rooty', 0.0))          # explicit (airborne) root height, 0 when not given
        F = build(p); params.append(p); figs.append(F); g.append(float(F.root_pos[1]))
    g = np.array(g)
    if smooth_ground and n > 2:
        # ground envelope: max filter then moving average -> smooth, never below the grounded height
        from scipy.ndimage import maximum_filter1d, uniform_filter1d
        w = max(3, int(round(0.25 * fps)))
        env = uniform_filter1d(maximum_filter1d(g, size=2 * w + 1, mode='nearest'), size=2 * (w // 2) + 1, mode='nearest')
        env = np.maximum(env, g)
    else:
        env = g
    rooty = np.maximum(env, np.array(air))
    # pass 2: render (frames are independent -> optional process pool)
    global _JOB
    caps = []
    for i in range(n):
        t = min(i / fps, times[-1])
        figs[i].root_pos[1] = rooty[i]; figs[i].fk()
        cur = [l for l, tk in zip(labels, times) if l and tk <= t + 1e-9]
        caps.append(cur[-1] if cur else None)
    _JOB = dict(figs=figs, props=props, cam=cam, W=W, H=H, fit_figs=fit_figs, mat=mat is None, tint=tint, caps=caps)
    if workers and workers > 1:
        import multiprocessing as mp
        with mp.get_context('fork').Pool(workers) as pool:
            raw = pool.map(_render_frame, range(n), chunksize=1)
    else:
        raw = [_render_frame(i) for i in range(n)]
    _JOB = None
    frames = [Image.open(io.BytesIO(b)).convert('P', palette=Image.ADAPTIVE, colors=colors) for b in raw]
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=gif_durations(len(frames), fps), loop=0, optimize=True)
    enc = write_mp4(os.path.splitext(path)[0] + '.mp4', raw, fps)
    print(f'{len(frames)} frames at {fps} fps ({len(frames) / fps:.1f} s); mp4 encoder: {enc}')
    return path
