#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = [
# "licofage",
# ]
# ///
import stat
from argparse import ArgumentParser, FileType
from licofage.argmisc import Formatter
from licofage.kit import *
from os import environ
import datetime
from pathlib import Path as P
from tempfile import TemporaryDirectory
from shutil import make_archive

today = datetime.date.today().strftime("%Y-%m-%d")
parser = ArgumentParser(
    prog="gen_abcomp",
    description="""Abelian Compexity Generator

Generates a qmd file to compute the k-abelian complexity of a given substitution for values of k in an interval.

It assumes that the 2-block substitution is Pisot and tries to compute automatic sequences for the complexities.

Typical usage: $ ./gen_abcomp -f 1 -t 5 tri '01/02/0'""",
    formatter_class=Formatter,
)

parser.add_argument(
    "-f",
    "--from",
    type=int,
    dest="start",
    default=1,
    help="first k-abelian complexity to compute (default to 1)",
)
parser.add_argument(
    "-t",
    "--to",
    type=int,
    dest="end",
    default=4,
    help="last k-abelian complexity to compute (default to 4)",
)
parser.add_argument(
    "-o",
    "--output",
    type=FileType("w"),
    default=None,
    help="output file (default to [name].qmd)",
)
parser.add_argument(
    "-z",
    "--zip",
    action="store_true",
    help="create zipped Walnut instance instead of notebook",
)
parser.add_argument(
    "-u", "--unroll", action="store_true", help="unroll Walnut scripts"
)
parser.add_argument(
    "-v", "--verbose", action="store_true", help="display more messages"
)
parser.add_argument(
    "-S", "--stats", action="store_true", help="display statistics about computations"
)
parser.add_argument("name", help="numeration system and fixpoint naming")
parser.add_argument("subst", help="substitution considered")
parser.add_argument(
    "fullname", help="full name of the studied sequence (for the title)", default=None
)
args = parser.parse_args()

if args.zip:
    tmpdir = TemporaryDirectory()
    basedir = P(tmpdir.name) / args.name
    basedir.mkdir()
    walnutdir = basedir / "Walnut"
    walnutdir.mkdir()
    for s in "Result,Command Files,Custom Bases,Automata Library,Word Automata Library".split(
        ","
    ):
        (walnutdir / s).mkdir()
    walnut_out = open(walnutdir / "Command Files" / "gen_abcomp.txt", "w")
    py_out = open(basedir / "prelim.py", "w")

if not args.zip and args.output is None:
    args.output = open(f"{args.name}.qmd", "w")

if args.fullname is None:
    args.fullname = args.name.title()

out = args.output


def expelliarmus(s):
    if not args.zip:
        out.write(s)


def pytron(s):
    if args.zip:
        py_out.write(s)
        py_out.write("\n")
    else:
        out.write(f"""
```{walnut}
%%python
{s}
```
""")

genv = dict()

def pytronu(s, ss=None):
    global genv
    if args.unroll:
        exec(s, genv)
    pytron(f"{s}\n{ss}" if ss is not None else s)

def waltron(s):
    if args.zip:
        walnut_out.write(s)
        walnut_out.write("\n")
    else:
        out.write(f"""
```{walnut}
{s}
```
""")


def scriptron(sname, py):
    global genv
    if args.unroll:
        genv["script"] = []
        exec(py, genv)
        waltron("\n".join(genv["script"]))
    else:
        pytron(f"""script = []
{py}
writefile(f"{sname}", "\\n".join(script))""")
        waltron(f"""load {sname}.txt;""")


expelliarmus(f"""---
title: k-Abelian Complexity of {args.fullname} from {args.start} to {args.end}
date: '{today}'
format:
  html:
    code-fold: false
    embed-resources: true
    toc: true
    toc-location: left
    number-sections: true
    syntax-definitions: 
        - walnut.xml
  ipynb: default 
execute:
  cache: true
  keep-ipynb: true
  allow_errors: true
jupyter: walnut
---
""")

walnut = "{walnut}"
name = args.name
base = f"msd_{name}"
word = name.title()

### Initial setup

expelliarmus(f"""
## Initial Numeration System Setup

First we define the subsitution, its numeration system and its fixpoint sequence.
""")
pytronu(f"""from licofage.kit import *
import os
setparams({repr(args.verbose)}, {repr(args.stats)}, os.environ["WALNUT_HOME"])

s = subst({repr(args.subst)})
ns = address(s, "{name}")""", 
"""ns.gen_ns()
ns.gen_word_automaton()""")

expelliarmus(f"""
Then we setup a factor comparison predicate in Walnut and a first factor occurence predicate.
""")

waltron(f"""def cut "?{base} i<=u & j<=v & u+j=v+i & u<n+i & v<n+j":
def feq_{name} "?{base} ~(Eu,v $cut(i,j,n,u,v) & {word}[u]!={word}[v])":
eval comp_{name} n "?{base} Aj $feq_{name}(i,j,n) => i<=j":""")

expelliarmus(f"""

From there we can define the boundary condition `bordercond`, as explained in Fici-Puzynina-2023 section 8.1.
""")

waltron(
    f"""def bordercond "?{base} (k<=n => $feq_{name}(i,j,k-1)) & (n<k => $feq_{name}(i,j,n))":"""
)

for cur in range(args.start, args.end + 1):
    cname = f"{name}b{cur}"
    cbase = f"msd_{cname}"
    cword = cname.title()
    cborder = f"bordercond{cur}"
    if cur == 1:
        cbase = base
        cword = word
        cborder = "bordercond"
    expelliarmus(f"""
## {cur}-abelian complexity

Define the {cur}-block map of {name} and construct the conversion predicate between both numeration systems.
""")
    if cur == 1:
        pytronu(f"""s{cur} = s
ns{cur} = ns""")
    else:
        pytronu(f"""s{cur} = block(s, {cur})
ns{cur} = address(s{cur}, "{cname}")""",
        f"""ns{cur}.gen_ns()
(ns-ns{cur}).gen_dfa("conv_{name}_{cname}")""")
        expelliarmus(f"""
Translate the border condition predicate into the current numeration system.
""")
    if cur > 1:
        waltron(f"""def {cborder} "?{cbase} (?{base} Eii,jj,kk,nn 
($conv_{name}_{cname}(?{base} ii, ?{cbase} i) & 
$conv_{name}_{cname}(?{base} jj, ?{cbase} j) & 
$conv_{name}_{cname}(?{base} kk, ?{cbase} k) & 
$conv_{name}_{cname}(?{base} nn, ?{cbase} n) & 
$bordercond(ii,jj,kk,nn)))":""")
    expelliarmus(f"""
### Compute Parikh vectors

First we compute the Parikh vectors for the prefixes of {cword}.
""")
    pytron(f"""for (i,a) in enumerate(ns{cur}.alpha):
    w = {{'_': 0}}
    w[a] = 1
    parikh = address(s{cur}, ns{cur}.ns, **w)
    (parikh - ns{cur}).gen_dfa(f"{cname}p{{i}}")""")
    expelliarmus(f"""
### Compute the complexity function

Use Walnut to generate a linear representation for the {cur}-abelian complexity.
""")
    scriptron(f"do_fac{cur}",
    f"""for (i,a) in enumerate(ns{cur}.alpha):
    script.append(f'''def fac{{i}} "?{cbase} Ex,y ${cname}p{{i}}(i,x) & ${cname}p{{i}}(i+n,y) & z+x=y":''')""")
    scriptron(f"do_min{cur}",
    f"""for (i,a) in enumerate(ns{cur}.alpha):
    script.append(f'''def min{{i}} "?{cbase} Ei $fac{{i}}(i,n,x) & Aj,y $fac{{i}}(j,n,y) => y>=x":''')""")
    scriptron(f"do_diff{cur}",
    f"""for (i,a) in enumerate(ns{cur}.alpha):
    script.append(f'''def diff{{i}} "?{cbase} Ex,y $min{{i}}(n,x) & $fac{{i}}(i,n,y) & z+x=y":''')""")
    scriptron(f"do_abeq{cur}",
    f"""ss = " & ".join([ f"(Ez $diff{{i}}(i,n,z) &  $diff{{i}}(j,n,z))" for (i,a) in enumerate(ns{cur}.alpha) ])
script.append(f'''def abeq_{name}{cur} "?{cbase} {{ss}}":''')""" if cur==1 else f"""ss = " & ".join([ f"(Ez $diff{{i}}(i,n,z) &  $diff{{i}}(j,n,z))" for (i,a) in enumerate(ns{cur}.alpha) ])
script.append(f'''def abeq_{cname} "?{cbase} ${cborder}(i,j,{cur},n+{cur-1}) & {{ss}}":
def abeq_{name}{cur} "?{base} (n<{cur-1} & $feq_{name}(i,j,n)) | (n>={cur-1} & (?{cbase} Eii,jj,nn ($conv_{name}_{cname}(?{base} i, ?{cbase} ii) & $conv_{name}_{cname}(?{base} j, ?{cbase} jj) & $conv_{name}_{cname}(?{base} n, ?{cbase} nn) & $abeq_{cname}(ii,jj,nn-{cur-1}))))":''')""")
    scriptron(f"do_comp{cur}",
    f"""script.append(f'''eval comp_{name}{cur} n "?{base} Aj $abeq_{name}{cur}(i,j,n) => i<=j":''')""")
    expelliarmus(f"""

### Apply the semigroup trick

```{walnut}
%SGT comp_{name}{cur} {base} Comp_{name}{cur}
```
""")

### Check it out!

expelliarmus(f"""## Check it out!


```{walnut}
%%python
from itertools import product
from ratser.walimp import from_walnut

def valid(a, h, u):
    cur=a
    for c in u:
        v = h[cur]
        if c >= len(v):
            return False
        cur = v[c]
    return True

def enumrepr(a, h, k):
    alpha=list(range(max(map(len,h.values()))))
    for u in product(alpha, repeat=k):
        if valid(a, h, u):
            yield ''.join(map(str,u))

l = []
lbl = []
for k in range({args.start},{args.end+1}):
    lbl.append(str(k))
    with open(P(os.environ["WALNUT_HOME"]) / P(f"Result/comp_{name}{{k}}.mpl")) as f:
            ser = from_walnut(f)
            l.append(ser)

(a,h)=s.subst()
print(f"{{'n':>4}}", *[f"{{x+'-ab({name})':>15}}" for x in lbl])
print('-'*(4+16*len(lbl)))
for (i, u) in enumerate(enumrepr(a, h, 8)):
    print(f"{{i:4}}", *[ f"{{int(s.value(u)):15}}" for s in l ])
```

""")

### Wrap it up!

expelliarmus(f"""## Let's wrap it up!

```{walnut}
%%shell
cd $WALNUT_HOME
cat << EOF | tr '\\n' '\\0' | tar cvzf /tmp/abelian.tar.gz --null -T -
Custom Bases/{base}.txt
Custom Bases/{base}_addition.txt
Word Automata Library/{word}.txt
Automata Library/feq_{name}.txt
Result/comp_{name}.mpl
""")
for cur in range(args.start, args.end + 1):
    cname = f"{name}b{cur}"
    expelliarmus(f"""Word Automata Library/Comp_{name}{cur}.txt
Result/comp_{name}{cur}.mpl
Automata Library/abeq_{name}{cur}.txt
""")
expelliarmus(f"""EOF
```


 {{{{< downloadthis /tmp/abelian.tar.gz dname="abelian.tar" >}}}}

""")

if args.zip:
    goscr = basedir / "go"
    with open(goscr, "w") as f:
        f.write("""#!/bin/sh
export WALNUT_MEM=64g
export WALNUT_HOME=$(pwd)/Walnut
uv run --python 3.12 --with licofage prelim.py
cd $WALNUT_HOME
echo "load gen_abcomp.txt;" | java -Xmx$WALNUT_MEM -jar $WALNUT_JAR 
""")
        for cur in range(args.start, args.end + 1):
            cname = f"{name}b{cur}"
            f.write(
                f"semitrick Result/comp_{name}{cur}.mpl {base} Word\\ Automata\\ Library/Comp_{name}{cur}.txt\n"
            )
        f.write(f"""cat << EOF | tr '\\n' '\\0' | tar cvzf ../abelian.tar.gz --null -T -
Custom Bases/{base}.txt
Custom Bases/{base}_addition.txt
Word Automata Library/{word}.txt
Automata Library/feq_{name}.txt
Result/comp_{name}.mpl
""")
        for cur in range(args.start, args.end + 1):
            cname = f"{name}b{cur}"
            f.write(f"""Word Automata Library/Comp_{name}{cur}.txt
Result/comp_{name}{cur}.mpl
Automata Library/abeq_{name}{cur}.txt
""")
        f.write("EOF\n")
    goscr.chmod(goscr.stat().st_mode | stat.S_IEXEC)
    walnut_out.close()
    py_out.close()
    make_archive(f"{args.name}", "zip", tmpdir.name, args.name)
    tmpdir.cleanup()
