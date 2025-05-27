#!/bin/bash
# Build with explicit backend specification for Python 3.12+
gfortran -O3 -Wall -c -fopenmp -fPIC tort.f90 

# For dist module - try with explicit backend
python -m numpy.f2py -c --opt='-O3' --f90flags='-fopenmp' -lgomp -m dist dist.f90

# For tort module - try with explicit backend  
python -m numpy.f2py -c --opt='-O3' --f90flags='-fopenmp' -lgomp -m _tort f90wrap_tort.f90 tort.o
