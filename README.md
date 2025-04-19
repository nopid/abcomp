# Generalized Abelian Complexity

This is the companion git repository for the paper *Effective Computation of Generalized Abelian Complexity for Pisot Type Substitutive Sequences*. It contains source code and supplementary material produced to prepare the paper. Please cite the above paper when reporting, reproducing or extending the results.


## Direct access with Binder

For immediate reproducibility of the code, one can access the content of this repository through Binder by entering the following URL in a webbrowser. This way, one can use Walnut with the provided artifacts and read the different notebooks provided in the repository.

https://mybinder.org/v2/gh/nopid/abcomp/main

The notebooks are in the notebooks/ directory.

## Sequences

Input and output files are provided for the following sequences, under the following names:
 
 - **fib** The Fibonacci sequence, Sturmian sequence, fixpoint of $0\mapsto 01,\; 1\mapsto 0$;
 - **pell** The Pell sequence, Sturmian sequence, fixpoint of $0\mapsto 001,\; 1\mapsto 0$;
 - **tri** The Tribonacci sequence, epiSturmian sequence, fixpoint of  $0\mapsto 01,\; 1\mapsto 02,\; 2\mapsto 0$;
 - **nara** The Narayana sequence, fixpoint of  $0\mapsto 01,\; 1\mapsto 2,\; 2\mapsto 0$;
 - **blop** fixpoint of  $0\mapsto 011,\; 1\mapsto 01$;
 - **muller** fixpoint of $0\mapsto 0001011,\; 1\mapsto 001011$;
 - **pof** fixpoint of $0\mapsto 001,\; 1\mapsto 201,\; 2\mapsto 0$;
 - **bpof** fixpoint of $0\mapsto 001,\; 1\mapsto 02,\; 2\mapsto 002$;
 - **spiral** fixpoint of $0\mapsto 001,\; 1\mapsto 2,\; 2\mapsto 02$;
 - **twi** The Twisted Tribonacci sequence, fixpoint of  $0\mapsto 01,\; 1\mapsto 20,\; 2\mapsto 0$;


## Numeration systems

The numeration systems are derived using the http://pypi.org/project/licofage/ tool. The basic files can be found inside the `*-abelian.tar.gz` output files from **section 4**, including custom numeration system, addition and factor equality predicate.


## Section 3

The `section3/` directory contains all the material to compute the two-dimensional generalized abelian complexity for uniformly-factor-bounded Pisot substitutive sequences.

see `section3/README.md` for detailled explanations.

## Section 4

The `section4/` directory contains the whole machinery to compute the $k$-abelian complexity for Pisot substitutions that satisfy the hypothesis in the paper.

Samples sources are in the `samples/` subdirectory and the files produced by running the computations are to be found in the `out/` subdirectory.

see `section4/README.md` for detailled explanations.
