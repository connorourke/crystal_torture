import unittest
from unittest.mock import Mock
from crystal_torture import Node, Cluster
from crystal_torture.pymatgen_interface import nodes_from_structure, clusters_from_file
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
        self.cluster = Cluster(set(self.mock_nodes)) 
        

#    def test_nodes_from_file(self):

        #structure = Structure.from_file("crystal_torture/tests/POSCAR_test.vasp")
        #nodes = nodes_from_structure(structure, 4.0, get_halo=False)
        #mock_neigh_ind = set([frozenset(node.neighbours_ind) for node in self.mock_nodes])
        #neigh_ind = set([frozenset(node.neighbours_ind) for node in nodes])

        #self.assertEqual(mock_neigh_ind,neigh_ind)
        #self.assertEqual(set([node.index for node in self.mock_nodes]),set([node.index for node in nodes]))
        #self.assertEqual(set([node.element for node in self.mock_nodes]),set([node.element for node in nodes]))

        #node=set()
        #node.add(nodes.pop())
        #cluster1 = Cluster(node)
        #cluster1.grow_cluster()
       # self.assertEqual(set([node.index for node in self.cluster.nodes]),set([node.index for node in cluster1.nodes]))
       # self.assertEqual(set([node.element for node in self.cluster.nodes]),set([node.element for node in cluster1.nodes]))

    def test_clusters_from_file(self): 
        
        clusters1 = clusters_from_file("crystal_torture/tests/POSCAR_2_cluster.vasp",4.0)
     #   for cluster in clusters1:
     #      print([node.index for node in cluster.nodes])
     #   clusters2  = clusters_from_file("crystal_torture/tests/POSCAR_2_cluster.vasp",3.5)
        self.assertEqual(len(clusters1),1)
    #    self.assertEqual(len(clusters2),2)
        
#    def test_cluster_periodic(self):
   
       # clusters1 = clusters_from_file("crystal_torture/tests/POSCAR_2_cluster.vasp",4.0)
       # clusters2  = clusters_from_file("crystal_torture/tests/POSCAR_2_cluster.vasp",3.5)
       # self.assertTrue([cluster.periodic[:] for cluster in clusters1])
       # if clusters2.pop().periodic == [False,False,False]:
       #    self.assertEqual(clusters2.pop().periodic,[True,True,True])
       # else:
       #    self.assertEqual(clusters2.pop().periodic,[False,False,False])



if __name__ =='__main__':
    unittest.main()

        

    
