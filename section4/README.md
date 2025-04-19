# Section 4. The case of Pisot substitutions

Welcome to the k-abelian complexity kit. To use this kit you will need a few pieces of software:
 - a java runtime command compatible with Java 17 jar (for Walnut);
 - the uv Python package manager (https://docs.astral.sh/uv/);
 - a few classical commands: make, realpath, mktemp, ...

The main script is `gen_abcomp.py`, a Python script that generates a qmd file to compute the k-abelian complexity of a given substitution for values of k in an interval. It assumes that the 2-block substitution is Pisot and tries to compute automatic sequences for the complexities. Alternatively, it can produce a zip archive instead of a qmd file, for remote execution with Walnut + Python/licofage.

The shell script `gen_samples` generates a bunch of examples in the `samples/` directory.

The shell script `render` is in charge of executing a qmd file, running Walnut and Python phases and rendering the output both as a notebook and as an HTML file with artifacts.

The `Makefile` automates the rendering of all qmd files in samples/ into out/

