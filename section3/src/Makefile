CC=clang++-mp-18 -Wno-deprecated-declarations -std=c++17 -O3 -fopenmp
CPPFLAGS=-DUSE_OPENMP -I/opt/local/include -I/opt/awali/include -I/opt/awali/share/awali/src
LDFLAGS=-L/opt/awali/lib -L/opt/local/lib

all: occ2equi first2comp difffirst pred2mat occ2equimat

%: %.cc walnut.hh reduce.hh gmpq.hh
	$(CC) $(CPPFLAGS) $(LDFLAGS) -o $@ $< /opt/local/lib/libgmpxx.a /opt/local/lib/libgmp.a
