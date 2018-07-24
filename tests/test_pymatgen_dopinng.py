import unittest
import copy
from unittest.mock import Mock
from crystal_torture import Node, Cluster, tort
from crystal_torture.pymatgen_doping import count_sites, dope_structure, dope_structure_by_no, sort_structure, index_sites
from pymatgen import Structure
from ddt import ddt, data, unpack

@ddt
class PymatgenDopingTestCase( unittest.TestCase ):
    """ Test simple doping routines"""

    def test_count_sites(self):

        structure = Structure.from_file("tests/STRUCTURE_FILES/POSCAR_SPINEL.vasp")
        structure.add_site_property("label",["A"]*8+["B"]*16+["O"]*32)

        self.assertEqual(count_sites(structure,species={"Mg"}),8)
        self.assertEqual(count_sites(structure,species={"Al"}),16)
        self.assertEqual(count_sites(structure,species={"O"}),32)
        self.assertEqual(count_sites(structure,species={"Li"}),0)
        self.assertEqual(count_sites(structure,labels={"A"}),8)
        self.assertEqual(count_sites(structure,labels={"B"}),16)
        self.assertEqual(count_sites(structure,labels={"O"}),32)
        self.assertEqual(count_sites(structure,labels={"Li"}),0)
        self.assertEqual(count_sites(structure,labels={"A","B","O"},species={"Mg","Al","O"}),56)

    @data(3,4,5,6)
    def test_doping(self,value):

        structure = Structure.from_file("tests/STRUCTURE_FILES/POSCAR_SPINEL.vasp")
        structure.add_site_property("label",["A"]*8+["B"]*16+["O"]*32)

        for conc in [0.5]:
            structure_temp = copy.deepcopy(structure)
            structure_temp.make_supercell([value,value,value])   
            dope_structure(structure_temp,conc,"Mg",["Li","Al"])
            doped_conc = count_sites(structure_temp,species={"Li","Al"},labels={"A"})/count_sites(structure_temp,labels={"A"})
            self.assertEqual(conc,doped_conc)

    @data(3,4,5,6)
    def test_doping_by_no(self,value):

        structure = Structure.from_file("tests/STRUCTURE_FILES/POSCAR_SPINEL.vasp")
        structure.add_site_property("label",["A"]*8+["B"]*16+["O"]*32)

        for no_dopants in [10,20,30,40]:
            structure_temp = copy.deepcopy(structure)
            structure_temp.make_supercell([value,value,value])
            dope_structure_by_no(structure_temp,no_dopants,"Mg",["Li","Al"],label_to_remove="A")
            dopants_Li = count_sites(structure_temp,species={"Li"},labels={"A"})
            dopants_Al = count_sites(structure_temp,species={"Al"},labels={"A"})
            self.assertEqual(no_dopants,dopants_Li)
            self.assertEqual(no_dopants,dopants_Al)
       
    
    def test_errors(self):

        structure = Structure.from_file("tests/STRUCTURE_FILES/POSCAR_SPINEL.vasp")
        structure.add_site_property("label",["A"]*8+["B"]*16+["O"]*32)

        with self.assertRaises(ValueError):
            dope_structure_by_no(structure,10,"P",["Li"])
        with self.assertRaises(ValueError):
            dope_structure(structure,10,"P",["Li"])
        with self.assertRaises(ValueError):
            count_sites(structure)
        with self.assertRaises(ValueError):
            sort_structure(structure,["Li","P","T"])
        with self.assertRaises(ValueError):
            index_sites(structure)
if __name__ =='__main__':
    unittest.main()

        

    
