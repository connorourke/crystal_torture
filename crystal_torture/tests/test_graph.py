import unittest
from unittest.mock import Mock
from crystal_torture import Cluster, Graph, Node

class GraphTestCase( unittest.TestCase ):
    """ Test for Graph Class"""

    def setUp( self ):
 
        cluster1 = Cluster([Mock(spec=Node),Mock(spec=Node),Mock(spec=Node),Mock(spec=Node)])
        cluster2 = Cluster([Mock(spec=Node),Mock(spec=Node),Mock(spec=Node),Mock(spec=Node)])
        
        self.clusters = [cluster1,cluster2]
        
        self.graph = Graph(self.clusters)

    def test_graph_is_initialised( self ):
        self.assertEqual( self.graph.clusters, self.clusters)
        self.assertEqual([c.nodes for c in self.graph.clusters],[c.nodes for c in self.graph.clusters]) 

            

if __name__ =='__main__':
    unittest.main()


