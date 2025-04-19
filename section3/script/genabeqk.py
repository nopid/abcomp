#!/usr/bin/env python3
import argparse
parser = argparse.ArgumentParser(
                    prog='genabeqk.py',
                    description='Produce script to compute the k-abelian complexity from the Diffabeq predicate')
parser.add_argument('ns', help="Numeration system")
parser.add_argument('n', type=int, help="k will vary from 1 to [n]")
parser.add_argument('v', type=int, help="Maximum value")
args = parser.parse_args()

wns = f"?msd_{args.ns}"
ns = args.ns

def peq(v, k='k', n='n'):
    return f"Diffabeq{ns}[{k}][{n}]=@{str(v)}"

s = ' | '.join(f"({peq(i)} & v={i})" for i in range(args.v))

print(f'def diffabeq{ns} "{wns} {s}":')
print(f'def abeq1{ns} "?msd_tri Ev $diffabeqtri(0,n,v) & w=v+1":')
for k in range(2,args.n+1):
    print(f'def abeq{k}{ns} "?msd_tri Eu,v $abeq{k-1}{ns}(n,u) & $diffabeqtri({k-1},n,v) & w=u+v":')
