#!/usr/bin/env python3
"""Render exercise scenes to PNG figures (with ghost outlines, arrows, viewpoint labels) and a contact sheet.

usage: compose.py --scenes SCENES.py --out FIG_DIR [--only 3 7 12]

SCENES.py must define SCENES = [(number, name, fn), ...] where fn() returns a scene dict
(see references/posing.md). The engine directory is put on sys.path, so scene files can
`from mannequin import *` and `from poselib import ...`.
"""
import sys, os, time, argparse, importlib.util
ENGINE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ENGINE)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import matplotlib.patheffects as pe
from PIL import Image, ImageDraw
from mannequin import render_scene, INK, MUTED, ACCENT

W, H = 1020, 740      # 51 x 37 mm at 20 px/mm
DPI = 200

def hexc(c):
    return '#%02x%02x%02x' % tuple(int(round(v * 255)) for v in c)

def _halo(artist, lw):
    artist.set_path_effects([pe.Stroke(linewidth=lw + 2.6, foreground='white', alpha=0.9), pe.Normal()])

def compose(scene, path, W=W, H=H):
    fit_pts = list(scene.get('fit_pts') or [])
    for a in scene.get('arrows', []):
        if a['kind'] == 'arrow':
            fit_pts += [a['p0'], a['p1']]
    R = render_scene(scene['figures'], scene.get('props', ()), cam=scene['cam'], W=W, H=H,
                     ghost_figures=scene.get('ghosts', ()), fit_pts=fit_pts, mat=scene.get('mat', True))
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')
    if scene.get('ghosts'):
        m = R.silhouette_of(scene['ghosts']).astype(float)
        fill = np.zeros((H, W, 4)); fill[..., :3] = MUTED; fill[..., 3] = 0.10 * m
        ax.imshow(fill, extent=[0, W, H, 0], zorder=1, interpolation='bilinear')
        ax.contour(m, levels=[0.5], colors=[hexc(MUTED)], linestyles='dashed', linewidths=1.5, zorder=1.5)
    ax.imshow(np.array(R.img), extent=[0, W, H, 0], zorder=2, interpolation='lanczos')
    for a in scene.get('arrows', []):
        s = a.get('size', 1.0); lw = 3.0 * s
        if a['kind'] == 'circ':
            cx, cy = R.project(a['c']); rpx = a['r'] * R.scale
            th = np.radians(np.linspace(a['a0'], a['a1'], 40))
            xs = cx + rpx * np.cos(th); ys = cy - rpx * 0.55 * np.sin(th)
            ln, = ax.plot(xs[:-1], ys[:-1], color=hexc(ACCENT), lw=lw, zorder=5, solid_capstyle='round')
            _halo(ln, lw)
            arr = FancyArrowPatch((xs[-3], ys[-3]), (xs[-1], ys[-1]), arrowstyle='-|>', mutation_scale=15 * s,
                                  lw=lw, color=hexc(ACCENT), zorder=5)
            _halo(arr, lw); ax.add_patch(arr)
            continue
        p0 = R.project(a['p0']); p1 = R.project(a['p1'])
        style = {'->': '-|>', '<-': '<|-', '<->': '<|-|>'}[a.get('style', '->')]
        arr = FancyArrowPatch(p0, p1, arrowstyle=style, connectionstyle=f"arc3,rad={a.get('rad', 0.0)}",
                              mutation_scale=15 * s, lw=lw, color=hexc(ACCENT), zorder=5,
                              capstyle='round', joinstyle='round')
        _halo(arr, lw); ax.add_patch(arr)
    if scene.get('label'):
        ax.text(14, H - 14, scene['label'], fontsize=7.5, color=hexc(MUTED), ha='left', va='bottom',
                fontfamily='DejaVu Sans', zorder=6)
    fig.savefig(path, dpi=DPI, transparent=True)
    plt.close(fig)
    return R

def load_scenes(path):
    spec = importlib.util.spec_from_file_location('scenes_mod', path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    spec.loader.exec_module(mod)
    return mod.SCENES

def contact_sheet(out_dir, names, path):
    files = sorted(f for f in os.listdir(out_dir) if f.endswith('.png') and f[:2].isdigit())
    tw, th, cols = 510, 370, 4
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw, rows * (th + 24)), 'white')
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        im = Image.open(os.path.join(out_dir, f)).convert('RGBA').resize((tw, th), Image.LANCZOS)
        x, y = (i % cols) * tw, (i // cols) * (th + 24)
        sheet.paste(im, (x, y + 24), im)
        n = int(f[:2])
        d.text((x + 6, y + 4), f'{n} {names.get(n, "")}', fill=(30, 30, 30))
        d.rectangle([x, y, x + tw - 1, y + th + 23], outline=(200, 200, 200))
    sheet.save(path)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--scenes', required=True)
    ap.add_argument('--out', default='figures')
    ap.add_argument('--only', nargs='*', type=int)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    SCENES = load_scenes(args.scenes)
    for n, name, fn in SCENES:
        if args.only and n not in args.only:
            continue
        t = time.time()
        scene = fn()
        compose(scene, os.path.join(args.out, f'{n:02d}.png'))
        F = scene['figures'][0]
        print(f'{n:2d} {name:34s} {time.time() - t:4.1f}s  lowest={F.lowest():+.3f}', flush=True)
    contact_sheet(args.out, {n: name for n, name, _ in SCENES}, os.path.join(args.out, 'sheet.png'))
    print('sheet:', os.path.join(args.out, 'sheet.png'))
