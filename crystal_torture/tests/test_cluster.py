import unittest
from unittest.mock import Mock
from crystal_torture.pymatgen_interface import nodes_from_structure, clusters_from_file
from crystal_torture import Cluster, Node

class ClusterTestCase( unittest.TestCase ):
    """ Test for Graph Class"""

    def setUp( self ):

        self.labels = ['A','B','O','A','B','O']
        self.elements = ["Mg","Al","O","Mg","Al","O"]
        self.node_ids = [ 0,1,2,3,4,5 ]
        self.neighbours = [[1,2,3,5],[0,2,4,5],[1,0,4,3],[0,4,5,2],[1,2,3,5],[4,3,0,1]]
        self.mock_nodes = [ Mock( spec=Node, index = i , element = e , labels = None , neighbours_ind = n, neigbours = None ) for i, e, l, n in zip(self.node_ids, self.elements, self.labels, self.neighbours)]
        
        for node in self.mock_nodes:
            node.neighbours = [self.mock_nodes[n] for n in node.neighbours_ind] 
            node.neighbours = set(node.neighbours)

        self.cluster1 = Cluster(set(self.mock_nodes[0:4]))
        self.cluster2 = Cluster(set(self.mock_nodes[3:7]))
    
        self.mock_nodes = set(self.mock_nodes)
        self.cluster = Cluster(self.mock_nodes)

    def test_cluster_is_initialised( self ):
        self.assertEqual( self.cluster.nodes, self.mock_nodes)
 
    def test_merge_cluster( self ):
        combined_cluster = self.cluster1.merge(self.cluster2)
        self.assertEqual(combined_cluster.nodes,self.mock_nodes)    

    def test_is_neighbour( self ):
        self.assertTrue(self.cluster1.is_neighbour(self.cluster2))

    def test_grow_cluster(self):
       
        self.cluster1.grow_cluster()
        self.assertEqual(self.cluster1.nodes,self.cluster.nodes)

    def test_torture_cluster(self):
        cluster =  clusters_from_file(filename="crystal_torture/tests/STRUCTURE_FILES/POSCAR_2_clusters.vasp",rcut=4.0,elements={"Li"})
        clusterf = cluster.pop()
        clusterf.grow_cluster()
        clusterf.torture_fort()
        self.assertEqual(set([node.tortuosity for node in clusterf.return_key_nodes(key="Halo",value=False)]),set([4,3,3,3,3,3,3,3]))

if __name__ =='__main__':
    unittest.main()


