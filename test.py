#! /usr/bin/env python3

from crystal_torture.pymatgen_interface import clusters_from_file
import time

clusters = clusters_from_file("crystal_torture/tests/POSCAR_2_cluster.vasp",4.0)

for cluster in clusters:
   if cluster.periodic > 0:
      time1=time.time()
      cluster.torture_fort()
      time2=time.time()
      print("Time",time2-time1)
