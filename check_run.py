#! /usr/bin/env python3


from pymatgen import Structure
spinel=Structure.from_file("examples/POSCAR_SPINEL.vasp")
spinel.add_site_property("label",["A"]*8+["B"]*16+["O"]*32)
spinel.make_supercell([3,3,3])
import crystal_torture.pymatgen_doping as pd

spinel = pd.dope_structure(spinel,conc=0.9,species_to_rem="Mg",species_to_insert=["Li","Al"],label_to_remove="A")


from crystal_torture.pymatgen_interface import graph_from_structure
graph = graph_from_structure(structure=spinel,rcut=4.0,elements={"Li"})
graph.torture()
