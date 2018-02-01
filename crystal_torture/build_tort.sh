#! /bin/bash
  gfortran -g -Wall -c -fopenmp  -fPIC tort.f90 
  f90wrap -v -m tort tort.f90 
  f2py-f90wrap -c --opt='-O3' --f90flags='-fopenmp' -lgomp -m _tort f90wrap_tort.f90 tort.o
  sed -i 's/import _tort/from crystal_torture import _tort/' tort.py
