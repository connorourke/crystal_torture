#! /usr/bin/env python3

from crystal_torture.pymatgen_interface import graph_from_file
import time

#graph = graph_from_file("crystal_torture/tests/STRUCTURE_FILES/POSCAR_UC.vasp",4.0,["Li"])
#graph = graph_from_file("POSCAR.vasp",4.0,["Li"])
#clusters = clusters_from_file("crystal_torture/tests/STRUCTURE_FILES/POSCAR_UC.vasp",4.0)
#graph = graph_from_file("crystal_torture/tests/STRUCTURE_FILES/POSCAR_SPINEL_SPLIT.vasp",4.0,["Li"])
graph = graph_from_file("crystal_torture/tests/STRUCTURE_FILES/POSCAR_8000.vasp",4.0,["Li"])

print("Got graph - torturing")

for cluster in graph.clusters:
   if cluster.periodic > 0:
      time1=time.time()
      cluster.torture_test()#_fort()
      time2=time.time()
      print("Time",time2-time1)
