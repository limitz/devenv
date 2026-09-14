"""Cat-cow loop: spine tweens between the cat and cow angles; hands and toes stay planted.
usage: python3 animate_catcow.py [out.gif]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from poselib import CAT, COW, catcow_figure, catcow_root_y
from animate import tween_loop

ry = catcow_root_y()
build = lambda s: catcow_figure(CAT + (COW - CAT) * s, ry)
out = sys.argv[1] if len(sys.argv) > 1 else 'cat-cow.gif'
print('wrote', tween_loop(build, out, N=36, fps=12, cam='side'))
