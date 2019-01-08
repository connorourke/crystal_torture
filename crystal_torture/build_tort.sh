#! /bin/bash
  gfortran -O3 -Wall -c -fopenmp  -fPIC tort.f90 
  f2py -c --opt='-O3' --f90flags='-fopenmp' -lgomp -m dist dist.f90
  f2py-f90wrap -c --opt='-O3' --f90flags='-fopenmp' -lgomp -m _tort f90wrap_tort.f90 tort.o
