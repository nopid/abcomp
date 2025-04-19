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
parser.add_argument('input', help="Walnut DFAO file")
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

with open(args.input) as f:
    d = dfa_from_walnut(f)

img = Image.new('RGB', (args.size, args.size))

for k in range(args.size):
    for n in range(args.size):
       img.putpixel((n, args.size - k - 1), colors[value(d, repair(k, n))%32])
img.save(args.output)
