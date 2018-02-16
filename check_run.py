#! /usr/bin/env python3

from crystal_torture.pymatgen_interface import graph_from_file, structure_from_cluster
import time

#graph = graph_from_file("crystal_torture/tests/STRUCTURE_FILES/POSCAR_UC.vasp",4.0,["Li"])
#graph = graph_from_file("POSCAR.vasp",4.0,["Li"])
#clusters = clusters_from_file("crystal_torture/tests/STRUCTURE_FILES/POSCAR_UC.vasp",4.0)
#graph = graph_from_file("crystal_torture/tests/STRUCTURE_FILES/POSCAR_SPINEL_SPLIT.vasp",4.0,["Li"])
#graph = graph_from_file("crystal_torture/tests/STRUCTURE_FILES/POSCAR_CUT.vasp",4.0,["Li"])
graph = graph_from_file("POSCAR_temp.vasp",4.0,["Li"])
print("Got graph - torturing")

for i,cluster in enumerate(graph.clusters):
   if cluster.periodic > 0:
      time1=time.time()
      cluster.torture_fort()
      print("Cluster av tort",cluster.tortuosity)
      time2=time.time()
      print("Time",time2-time1)
   clus_struct=structure_from_cluster(cluster,"POSCAR_temp.vasp")
   print(clus_struct)
   clus_struct.to(fmt='poscar',filename="TCLUS_"+str(i)+".vasp")

