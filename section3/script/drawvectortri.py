#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = [
# "Pillow",
# ]
# ///
from PIL import Image
import argparse
parser = argparse.ArgumentParser(
                    prog='drawtri.py',
                    description='Draw a tri-automatic 2D sequence')
parser.add_argument('input_dx', help="Walnut DFAO file")
parser.add_argument('input_dy', help="Walnut DFAO file")
parser.add_argument('dx', type=int, help="Picture vector dx")
parser.add_argument('dy', type=int, help="Picture vector dy")
parser.add_argument('size', type=int, help="Picture dimension")
parser.add_argument('output', help="Output image file")
args = parser.parse_args()

cur = (1, 2, 4)
trins = []
for _ in range(100):
    trins.append(cur[0])
    (x,y,z) = cur
    cur = (y,z,x+y+z)

def val(l):
    return sum([a*b for a,b in zip(reversed(l),trins)])

def repr(n):
    idx=0
    while trins[idx+1]<=n:
        idx+=1
    l=[]
    cur=n
    for v in reversed(trins[:idx+1]):
        if cur >= v:
            l.append(1)
            cur -= v
        else:
            l.append(0)
    return l

def repair(k,n):
    rk = repr(k)
    nk = len(rk)
    rn = repr(n)
    nn = len(rn)
    if nk < nn:
        rk = [0]*(nn-nk) + rk
    if nn < nk:
        rn = [0]*(nk-nn) + rn
    return list(zip(rk, rn))

colors = [ (173,216,230), (0,191,255), (30,144,255), (0,0,255), (0,0,139), (72,61,139), (123,104,238), (138,43,226), (128,0,128), (218,112,214), (255,0,255), (255,20,147), (176,48,96), (220,20,60), (240,128,128), (255,69,0), (255,165,0), (244,164,96), (240,230,140), (128,128,0), (139,69,19), (255,255,0), (154,205,50), (124,252,0), (144,238,144), (143,188,143), (34,139,34), (0,255,127), (0,255,255), (0,139,139), (128,128,128), (255,255,255) ]

def dfa_from_walnut(f):
    out=dict()
    trans=dict()
    cur=None
    curt=dict()
    next(f)
    for l in f:
        s=l.strip()
        if s=='': continue
        l=s.split('->')
        if len(l)==1:
            if cur is not None:
                trans[cur] = curt
                curt = dict()
            (q,o) = l[0].strip().split()
            cur = int(q)
            out[cur] = int(o)
        else:
            q=int(l[1].strip())
            a=tuple(map(int, l[0].split()))
            curt[a] = q
    if cur is not None:
        trans[cur] = curt
    return (trans, out)

def value(d, v):
    (trans, out) = d
    cur = 0
    for a in v:
        cur = trans[cur][a]
    return out[cur]

def vvalue(k, n):
    acc = 0
    if args.dx > 0:
        for z in range(args.dx):
            acc += value(dx, repair(k, n+z))
    if args.dy > 0:
        for z in range(args.dy):
            acc += value(dy, repair(k+z, n+args.dx))
    return acc

with open(args.input_dx) as f:
    dx = dfa_from_walnut(f)

with open(args.input_dy) as f:
    dy = dfa_from_walnut(f)

img = Image.new('RGB', (args.size, args.size))

miv =999999
mav = -999999
vals = set()
for k in range(0, args.size):
    for n in range(0, args.size):
       v = vvalue(k, n)
       vals.add(v)
       miv = min(v,miv)
       mav = max(v,mav)
       img.putpixel((n, args.size - k - 1), colors[v%32])
img.save(args.output)
print(f"min value : {miv}")
print(f"max value : {mav}")
print(f"values : {sorted(list(vals))}")
