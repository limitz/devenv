"""Tween a Figure between poses and write a looping GIF (and MP4 when ffmpeg is present).

    from animate import tween_loop
    tween_loop(build, 'cat-cow.gif', N=36, fps=12, cam='side')

`build(s)` returns a Figure for phase s in [0, 1]; the loop runs s: 0 -> 1 -> 0 with a cosine ease,
so build(0) is the start position and build(1) the end position. Framing is fixed from the two
extremes so the figure does not jump between frames. Keep the root fixed inside build() and use
arm_ik / leg_ik to pin hands and feet, exactly as for a still.
"""
import os, subprocess, shutil
import numpy as np
from PIL import Image
from mannequin import render_scene

def tween_loop(build, path, N=36, fps=12, cam='side', W=680, H=493, props=(), pingpong=True, colors=128):
    ext = [build(0.0), build(1.0)]
    frames = []
    for i in range(N):
        t = i / N
        s = 0.5 - 0.5 * np.cos(2 * np.pi * t) if pingpong else t
        R = render_scene([build(s)], props, cam=cam, W=W, H=H, ghost_figures=ext)
        im = Image.new('RGBA', R.img.size, (255, 255, 255, 255)); im.alpha_composite(R.img)
        frames.append(im.convert('P', palette=Image.ADAPTIVE, colors=colors))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=1000 // fps, loop=0, optimize=True)
    mp4 = os.path.splitext(path)[0] + '.mp4'
    if shutil.which('ffmpeg'):
        for enc in (['-c:v', 'libx264', '-crf', '20'], ['-c:v', 'libopenh264', '-b:v', '1500k'], ['-c:v', 'mpeg4', '-q:v', '3']):
            r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', path, '-vf',
                                f'fps={2 * fps},scale={W}:-2:flags=lanczos,format=yuv420p', *enc, '-movflags', '+faststart', mp4], stderr=subprocess.DEVNULL)
            if r.returncode == 0:
                break
    return path
