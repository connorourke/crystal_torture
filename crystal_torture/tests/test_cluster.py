import unittest
from unittest.mock import Mock
from crystal_torture import Cluster, Node

class ClusterTestCase( unittest.TestCase ):
    """ Test for Graph Class"""

    def setUp( self ):
 
        self.labels = ['A','B','O','A','B','O']
        self.elements = ["Mg","Al","O","Mg","Al","O"]
        self.node_ids = [ 1,2,3,4,5,6 ]
        self.neighbours = [[2,3,4,6],[1,3,5,6],[2,1,5,4],[1,5,6,3],[2,3,4,6],[5,4,1,2]]
        self.mock_nodes = [ Mock( spec=Node, index = i , element = e , labels = l , neighbours = n) for i, e, l, n in zip(self.node_ids, self.elements, self.labels, self.neighbours)]
        self.cluster = Cluster(self.mock_nodes)

    def test_cluster_is_initialised( self ):
        self.assertEqual( self.cluster.nodes, self.mock_nodes)
 


if __name__ =='__main__':
    unittest.main()


