import unittest
from unittest.mock import Mock
from crystal_torture import Node
from crystal_torture.pymatgen_interface import nodes_from_file
from pymatgen import Structure

class PymatgenTestCase( unittest.TestCase ):
    """ Test for interface with pymatgen"""
    
    def setUp(self):
        self.labels = ["Li"]*8
        self.elements = ["Li"]*8
        self.node_ids = list(range(9))
        self.neighbours_ind =[ set([2, 3, 6, 7]) ,
                               set([2, 3, 6, 7]) ,
                               set([0, 1, 4, 5]) ,
                               set([0, 1, 4, 5]) ,
                               set([2, 3, 6, 7]) ,
                               set([2, 3, 6, 7]) ,
                               set([0, 1, 4, 5]) ,
                               set([0, 1, 4, 5]) ]
        self.mock_nodes = [ Mock( spec=Node, index = i , element = e , labels = l , neighbours_ind = n, neigbours = None ) for i, e, l, n in zip(self.node_ids, self.elements, self.labels, self.neighbours_ind)]

        for node in self.mock_nodes:
            node.neighbours = [self.mock_nodes[n] for n in node.neighbours_ind]
            node.neighbours = set(node.neighbours)
        self.mock_nodes = set(self.mock_nodes)
        

    def test_nodes_from_file(self):

        nodes = nodes_from_file("crystal_torture/tests/POSCAR_test.vasp", 4.0)
        mock_neigh_ind = set([frozenset(node.neighbours_ind) for node in self.mock_nodes])
        neigh_ind = set([frozenset(node.neighbours_ind) for node in nodes])

        self.assertEqual(set([node.index for node in self.mock_nodes]),set([node.index for node in nodes]))
        self.assertEqual(set([node.element for node in self.mock_nodes]),set([node.element for node in nodes]))
        self.assertEqual(mock_neigh_ind,neigh_ind)

if __name__ =='__main__':
    unittest.main()

        

    
