# Section 3. The case of Pisot substitutions

Let Foo be a foo-automatic word. We are interested in computing the 2D foo-regular sequence that computes the k-abelian complexity of Foo for factors of size n. We assume that Foo is uniformly-factor-balanced: the difference of the number of occurrences for any word within any two positions of Foo is uniformly bounded by a constant.

The numeration systems basic files are to be found inside section 4 subdirectory.

The different files are organized as follows:
 - subdirectory `input/` contains various Walnut scripts;
 - subdirectory `src/` contains the C++ source code (requires Awali 2.3);
 - subdirectory `script/` contains some Python scripts;
 - subdirectory `out/` contains the logs and files produced.


# Implementing Lemma 6

## 1. input/gen_occ.txt

`def occ_foo "?msd_foo j1<=u & u<=j1+n & $feq_foo(i,u,k) & j2=j2":`

The predicate `occ_foo(i,j1,j2,k,n,u)` asserts that all 6 variables are valid in `msd_foo`, that u lies in between j1 and j1+n and that both factors of size k starting from i and u are equal.

See `out/gen_occ.log` and `out/gen_occ.tar.xz`.

## 2. src/occ2equi

Assuming uniformly-factor-balancedness, we derive from `occ_foo.txt` (the dfa that computes `occ_foo`) an automatic word `Equifoo.txt` such that `Equifib[i][j1][j2][k][n]` is the difference of the number of occurrences of `Foo[i..i+k[` between `Foo[j2..j2+n+k[` and `Foo[j1..j1+n+k[`.

To do this, `src/occ2equi.cc` does the following:
 1. load `occ_foo.txt`
 2. compute the foo-regular representation that counts `u` such that `occ_foo(i,j1,j2,k,n)`, gives us s1
 3. swap `j1` and `j2` to compute s2
 4. compute t = s1-s2
 5. use the semigroup trick to get a DFAO for t

See `out/equi.tar.xz` and `out/equi*.log`


# Implementing Lemma 7

## 3. scripts/checkequi.py

Rename `Equifoo.txt` to `Dequifoo.txt` because Walnut doesn't like E as the first letter. The `checkequi.py` script is there to help us prove inductively that we have indeed computed the right quantity! This gives us a *proof* that Foo is uniformly-factor-C-equilibrated and lets us compute the fine C bounds.

See `input/check_*.txt` and `out/check_*.log`


# Implementing Lemma 8

## 4. input/gen_abeq.txt

We can now define the predicate that computes the abelian equivalence `abeqfoo(i,j,k,n)` :
 1. define `samefoo(i,j1,j2,k,n)` if `Foo[j1..j1+n+k[` and `Foo[j2..j2+n+k[` have the same number of occurrences of `Foo[i.i+k[`
 2. define `abeqexfoo(j1,j2,n)` if `Foo[j1..j1+n+k[` and `Foo[j2..j2+n+k[' have the same number of occurrences of any word of size `k`
 3. derive `abeqfoo(i,j,k,n)` if `Foo[i..i+n[` and `Foo[j..j+n[` are $k$-abelian equivalents.

See `out/gen_abeq.tar.xz` and `out/gen_abeq.log`

## 5. input/abcomp.txt

We have the equivalence, from there we define the first occurrences and we can count to get the regular representation using `src/first2comp`. We compute two of them :
 - `abfirstfoo(i,k,n)` is the classical first occurrence
 - `abfirstsfoo(i,j,k,n)` is just `abfirstfoo(i,k+1,n)` (to be used with `difffirst`).

We do have the abelian complexity in the regular counting representation of `abfirstfoo`. For sturmian, this is not really interesting. For tri the 4 matrices are 264x264.

See `out/abcomp.tar.xz`, `out/abcomp.log`, `out/abcomp_*.txt` and `out/matri.sage`

# Complements for Tribonacci

## 6. src/difffirst

When `abcomp(k+1,n) - abcomp(k,n)` is bounded (and this is the case for Tribonacci for example!), we use `src/difffirst.cc` to get a foo-automatic representation of that quantity. The idea is the same as for `src/occ2equi`.

## 7. scripts/genabeqk.py

From the previous foo-automatic predicate we can compute efficiently and recursively a predicate for the k-abelian complexity!

See `input/gen_trikabeq.txt`, `out/gen_trikabeq.log` and `out/gen_trikabeq.tar.xz`

## 8. pictures

For Tribonacci, `abcomp(k, n+1) - abcomp(k, n)` is also bounded, as it is automatic, so we can derive efficiently predicates to compute k -> abcomp(k,n) for fixed n.

We can even draw pictures from these tri-automatic 2D words to try to understand their structure.

See `out/diffztri.tar.xz`, `scripts/draw*.py` and `out/Diff*tri*.png`

