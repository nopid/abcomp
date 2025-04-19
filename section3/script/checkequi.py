#!/usr/bin/env python3
import argparse
parser = argparse.ArgumentParser(
                    prog='checkequi.py',
                    description='Produce check script for the predicate produced by occ2equi')
parser.add_argument('ns', help="Numeration system")
parser.add_argument('v', type=int, help="Maximum value")
parser.add_argument('-p', '--prefix', default="Dequi", help="Walnut predicate prefix")
args = parser.parse_args()

p = f"{args.prefix}{args.ns}"
wns = f"?msd_{args.ns}"
ns = args.ns

def peq(v, i='i', j1='j1', j2='j2', k='k', n='n'):
    return f"Dequi{ns}[{i}][{j1}][{j2}][{k}][{n}]=@{str(v)}"

s = ' | '.join(peq(i, n='0') for i in [-1,0,1])
print(f'eval init "{wns} Ai,j1,j2,k {s}":')
print(f"""
eval initXX "{wns} Ai,j1,j2,k ($feq_{ns}(i,j1,k) <=> $feq_{ns}(i,j2,k)) <=> {peq(0, n='0')}":
eval initTF "{wns} Ai,j1,j2,k ($feq_{ns}(i,j1,k) & ~$feq_{ns}(i,j2,k)) <=> {peq(1, n='0')}":
eval initFT "{wns} Ai,j1,j2,k (~$feq_{ns}(i,j1,k) & $feq_{ns}(i,j2,k)) <=> {peq(-1, n='0')}":
""")

s = ' | '.join([f"({peq(i)} & {peq(i+1,n='n+1')})" for i in range(-args.v, args.v)])
print(f'def increase "{wns} {s}":')
s = ' | '.join([f"({peq(i+1)} & {peq(i,n='n+1')})" for i in range(-args.v, args.v)])
print(f'def decrease "{wns} {s}":')
s = ' | '.join([f"({peq(i)} & {peq(i,n='n+1')})" for i in range(-args.v, args.v+1)])
print(f'def constant "{wns} {s}":')

print(f"""
eval nxt "{wns} Ai,j1,j2,k,n $constant(i,j1,j2,k,n) | $increase(i,j1,j2,k,n) | $decrease(i,j1,j2,k,n)":
eval nxtXX "{wns} Ai,j1,j2,k,n ($feq_{ns}(i,j1+n+1,k) <=> $feq_{ns}(i,j2+n+1,k))  <=> $constant(i,j1,j2,k,n)":
eval nxtTF "{wns} Ai,j1,j2,k,n ($feq_{ns}(i,j1+n+1,k) & ~$feq_{ns}(i,j2+n+1,k)) <=> $increase(i,j1,j2,k,n)":
eval nxtFT "{wns} Ai,j1,j2,k,n (~$feq_{ns}(i,j1+n+1,k) & $feq_{ns}(i,j2+n+1,k)) <=> $decrease(i,j1,j2,k,n)":
""")


