import unittest
from unittest.mock import Mock
from crystal_torture import Cluster, Graph, Node, tort
from crystal_torture.pymatgen_interface import graph_from_file, clusters_from_file

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
        self.graph = Graph({self.cluster})

    def test_graph_is_initialised( self ):
        self.cluster.grow_cluster()
        graph = Graph({self.cluster})

        c_nodes = set([node.index for node in self.cluster.nodes])
        g_nodes = set([node.index for node in graph.clusters.pop().nodes])

        self.assertEqual( g_nodes, c_nodes)

    def test_graph_from_file(self):
#        tort.tort_mod.tear_down()

        graph = graph_from_file(filename="crystal_torture/tests/STRUCTURE_FILES/POSCAR_2_clusters.vasp",rcut=4.0, elements={"Li"})
        tort.tort_mod.tear_down()

        clusters = clusters_from_file(filename="crystal_torture/tests/STRUCTURE_FILES/POSCAR_2_clusters.vasp",rcut=4.0,elements={"Li"})
        tort.tort_mod.tear_down()
        c_nodes = set([node.index for node in clusters.pop().nodes])
        g_nodes = set([node.index for node in graph.clusters.pop().nodes])

        self.assertEqual( g_nodes,c_nodes)
            

if __name__ =='__main__':
    unittest.main()


