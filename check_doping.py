#! /usr/bin/env python3

import crystal_torture.pymatgen_doping as pd
from crystal_torture.pymatgen_interface import graph_from_file, structure_from_cluster
from pymatgen import Structure
import time
import sys

spinel_unit=Structure.from_file("crystal_torture/tests/STRUCTURE_FILES/POSCAR_SPINEL.vasp")
spinel_unit.add_site_property("label",["A"]*8+["B"]*16+["O"]*32)
spinel_unit.remove_species(["Al","Si","O"])
spinel_unit.make_supercell([14,14,14])


#print(pd.count_sites(spinel_unit,species={"Al"},labels={"A"}))
#print(pd.index_sites(spinel_unit,species={"Al"},labels={"B"}))




spinel_unit = pd.dope_structure(spinel_unit,conc=0.8,species_to_rem="Mg",species_to_insert=["Li","Al"],label_to_remove="A")

spinel_unit.remove_species(["Mg","Al"])
#spinel_unit = pd.dope_structure(spinel_unit,conc=0.6,species_to_rem="Al",species_to_insert=["Si","Si","Si","X0+"])



spinel_unit = pd.sort_structure(spinel_unit,["Li","X0+","Mg","Al","Si","O"])
spinel_unit.to(filename="POSCAR_full.vasp")

#structure = pd.dope_structure(spinel_unit,conc=0.25,species_to_rem="Mg",species_to_insert="Al",label_to_remove="A")
#structure = pd.dope_structure(spinel_unit,conc=0.5,species_to_rem="Al",species_to_insert="Si",label_to_remove="B")
#structure = pd.dope_structure(spinel_unit,conc=0.6,species_to_rem="Al",species_to_insert="X0+",label_to_remove="A")


#spinel_unit.remove_species(["Al","Si","Mg","O"])
spinel_unit = pd.sort_structure(spinel_unit,["Li","X0+"])


spinel_unit.to(filename="POSCAR.vasp")

graph = graph_from_file(filename="POSCAR.vasp",rcut=4.0,elements=["Li","X"])


graph.torture()
 
graph.output_clusters(fmt='poscar',graph_structure=spinel_unit,periodic=False)

for cluster in graph.minimal_clusters:
    print("**************") 
    print(cluster.size)
    print(cluster.tortuosity)
    print(cluster.periodic)

print(graph.return_frac_percolating())
#print(graph.tortuosity)
