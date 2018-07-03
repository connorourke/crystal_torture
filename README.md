
### Status
[![Build Status](https://travis-ci.com/connorourke/crystal_torture.png?branch=master)](https://travis-ci.org/connorourke/crystal_torture?branch=master)

Wrapping and compiling fortran with derived types:


compiling dist.f90:
f2py -c --opt='-O3' --f90flags='-fopenmp' -lgomp -m dist dist.f90



and for the tort.f90 case:

 gfortran -c -O3 -fPIC tort.f90
 f90wrap -v -m tort tort.f90
 f2py-f90wrap -c --opt='-O3' --f90flags='-fopenmp' -lgomp -m _tort f90wrap_tort.f90 tort.o





need to change the import statement in the produced tort.py to:

from crystal_torture import _tort



then import in cluster like:

from crystal_torture import tort

and access like:

tort.tort_mod.torture(n=4)

