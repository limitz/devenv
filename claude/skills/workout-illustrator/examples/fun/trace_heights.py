"""Trace the grounded root height per frame of a sequence demo and flag floor sweeps (spikes).
usage: python3 trace_heights.py [demo.py]"""
import os
import sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
f=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lyrical.py')
src=open(f).read(); src=src[:src.index("out = sys.argv")]
ns={'__file__': f}; exec(compile(src,'lyrical','exec'),ns)
from animate import _monotone_tangents, _hermite, param_pose
from mannequin import Figure
K=[(t, {k:v for k,v in p.items() if k!='label'}) for t,p in ns['K']]
keys=sorted(set(k for _,p in K for k in p)); times=np.array([t for t,_ in K]); full=[{k:p.get(k,0.0) for k in keys} for _,p in K]
tang={k:_monotone_tangents(times,np.array([f_[k] for f_ in full])) for k in keys}
g=[]; ts=[]
for i in range(int(times[-1]*12)+1):
    t=min(i/12,times[-1]); j=max(0,min(len(times)-2,np.searchsorted(times,t,side='right')-1))
    p={k: float(_hermite(times,np.array([f_[k] for f_ in full]),tang[k],j,t)) for k in keys}
    F=Figure(param_pose(p), root_pos=(p.get('x',0),0.96,p.get('z',0))); F.ground(); g.append(F.root_pos[1]); ts.append(t)
g=np.array(g); ts=np.array(ts)
kh=np.array([float(Figure(param_pose(p), root_pos=(0,0.96,0)).root_pos[1]-Figure(param_pose(p), root_pos=(0,0.96,0)).lowest()) for _,p in K])
print('keyframe heights:', ' '.join(f'{t}:{h:.2f}' for t,h in zip(times,kh)))
ref=np.interp(ts,times,kh); sp=g-ref
print('spikes > 8cm:', [f'{t:.2f}(+{v:.2f})' for t,v in zip(ts,sp) if v>0.08] or 'none')
print('max frame-to-frame change: %.3f m' % np.abs(np.diff(g)).max())
