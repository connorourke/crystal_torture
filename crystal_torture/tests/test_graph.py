import unittest
from unittest.mock import Mock
from crystal_torture import Cluster, Graph, Node

class GraphTestCase( unittest.TestCase ):
    """ Test for Graph Class"""

    def setUp( self ):
 
        self.labels = ['A','B','O','A','B','O']
        self.elements = ["Mg","Al","O","Mg","Al","O"]
        self.node_ids = [ 0,1,2,3,4,5 ]
        self.neighbours = [[1,2,3,5],[0,2,4,5],[1,0,4,3],[0,4,5,2],[1,2,3,5],[4,3,0,1]]
        self.nodes = [ Mock( spec=Node, index = i , element = e , labels = l , neighbours_ind = n, neigbours = None ) for i, e, l, n in zip(self.node_ids, self.elements, self.labels, self.neighbours)]

        for node in self.nodes:
            node.neighbours = [self.nodes[n] for n in node.neighbours_ind]
            node.neighbours = set(node.neighbours)

        self.cluster = Cluster({self.nodes.pop()})
       # self.cluster.grow_cluster()
        self.graph = Graph({self.cluster})

    def test_graph_is_initialised( self ):
        cluster = Cluster({self.nodes.pop()})
        #cluster.grow_cluster()
       # graph = Graph({cluster})
       # self.assertEqual( graph.clusters.pop().nodes, self.graph.clusters.pop().nodes)

            

if __name__ =='__main__':
    unittest.main()


