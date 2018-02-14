#! /usr/bin/env python3

import crystal_torture.pymatgen_doping as pd
from crystal_torture.pymatgen_interface import graph_from_file
from pymatgen import Structure
import time

spinel_unit=Structure.from_file("crystal_torture/tests/STRUCTURE_FILES/POSCAR_SPINEL.vasp")
spinel_unit.add_site_property("label",["A"]*8+["B"]*16+["O"]*32)
spinel_unit.make_supercell([3,3,3])


print(pd.count_sites(spinel_unit,species={"Al"},labels={"A"}))
print(pd.index_sites(spinel_unit,species={"Al"},labels={"B"}))




spinel_unit = pd.dope_structure(spinel_unit,conc=0.55,species_to_rem="Mg",species_to_insert=["Li","Li"],label_to_remove="A")

#spinel_unit = pd.dope_structure(spinel_unit,conc=0.6,species_to_rem="Al",species_to_insert=["Si","Si","Si","X0+"])



spinel_unit = pd.sort_structure(spinel_unit,["Li","X0+","Mg","Al","Si","O"])
spinel_unit.to(filename="POSCAR_full.vasp")


#structure = pd.dope_structure(spinel_unit,conc=0.25,species_to_rem="Mg",species_to_insert="Al",label_to_remove="A")
#structure = pd.dope_structure(spinel_unit,conc=0.5,species_to_rem="Al",species_to_insert="Si",label_to_remove="B")
#structure = pd.dope_structure(spinel_unit,conc=0.6,species_to_rem="Al",species_to_insert="X0+",label_to_remove="A")


spinel_unit.remove_species(["Al","Si","Mg","O"])
spinel_unit = pd.sort_structure(spinel_unit,["Li","X0+"])


spinel_unit.to(filename="POSCAR.vasp")

graph = graph_from_file(filename="POSCAR.vasp",rcut=4.0,elements=["Li","X"])


for index,cluster in enumerate(graph.clusters):
   print("CLuster periodic",cluster.periodic,"no nodes in cluster",len(cluster.nodes))
   print("index list",[node.index for node in cluster.nodes])
   print("uc index list",[node.index for node in cluster.return_key_nodes(key="Halo",value=False)])

   if cluster.periodic > 0:
      print("about to allocate")
      cluster.torture_fort()
      print("Tortuosity:",cluster.tortuosity)

   
print(spinel_unit)
