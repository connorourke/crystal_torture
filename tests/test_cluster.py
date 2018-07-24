import unittest
from unittest.mock import Mock
from crystal_torture.pymatgen_interface import nodes_from_structure, clusters_from_file, graph_from_file
from crystal_torture import Cluster, Node, tort, Graph
from ddt import ddt, data, unpack

@ddt
class ClusterTestCase( unittest.TestCase ):
    """ Test for Cluster Class"""

    def setUp( self ):

        self.labels = ["A","B", "O", "A", "B", "O"]
        self.elements = ["Mg","Al","O","Mg","Al","O"]
        self.node_ids = [ 0,1,2,3,4,5 ]
        self.neighbours = [[1,2,3,5],[0,2,4,5],[1,0,4,3],[0,4,5,2],[1,2,3,5],[4,3,0,1]]
        self.mock_nodes = [ Mock( spec=Node, index = i , element = e , labels = {"site label":l} , neighbours_ind = n, neigbours = None ) for i, e, l, n in zip(self.node_ids, self.elements, self.labels, self.neighbours)]
        
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

    def test_return_uc_indices(self):

        graph = graph_from_file(filename="tests/STRUCTURE_FILES/POSCAR_SPINEL.vasp",rcut=4.0,elements={"Mg"})
        self.assertEqual(graph.clusters.pop().return_uc_indices(),{'0','1','2','3','4','5','6','7'})

    def test_return_index_node(self):

        nodes = set([self.cluster1.return_index_node(0),
                     self.cluster1.return_index_node(1),
                     self.cluster1.return_index_node(2),
                     self.cluster1.return_index_node(3)])

        self.assertEqual(nodes,self.cluster1.nodes)

    def test_grow_cluster_key(self):
      
        self.cluster1.grow_cluster(key='site label', value = 'A')
        indices = set([node.index for node in self.cluster1.return_key_nodes(key='site label', value = 'A')])
        self.assertEqual(indices,{0,3})

    @data("POSCAR_2_clusters.vasp")
    def test_torture_cluster(self, value):
        cluster =  clusters_from_file(filename="tests/STRUCTURE_FILES/" + value,rcut=4.0,elements={"Li"})
        clusterf = cluster.pop()
        clusterf.grow_cluster()
        clusterf.torture_fort()
        tort.tort_mod.tear_down()

        self.assertEqual(set([node.tortuosity for node in clusterf.return_key_nodes(key="Halo",value=False)]),set([4,3,3,3,3,3,3,3]))

    @data("POSCAR_2_clusters.vasp")
    def test_minimal_cluster(self, value):
        
        graph = graph_from_file(filename="tests/STRUCTURE_FILES/" + value,rcut=4.0,elements={"Li"})

        cluster =  clusters_from_file(filename="tests/STRUCTURE_FILES/" + value,rcut=4.0,elements={"Li"})
        clusterf = cluster.pop()
        clusterf.grow_cluster()
        clusterf.torture_fort()
        graph.torture()

        self.assertEqual(set([c.tortuosity for c in graph.minimal_clusters]),set([c.tortuosity for c in list(graph.clusters)]))

    @data("POSCAR_2_clusters.vasp")
    def test_py_equals_fort(self,value):
        graph_p = graph_from_file(filename="tests/STRUCTURE_FILES/" + value,rcut=4.0,elements={"Li"})
        graph_p.torture_py()

        graph_f = graph_from_file(filename="tests/STRUCTURE_FILES/" + value,rcut=4.0,elements={"Li"})
        graph_f.torture()

        self.assertEqual([c.tortuosity for c in list(graph_p.clusters)],[c.tortuosity for c in list(graph_f.clusters)])

if __name__ =='__main__':
    unittest.main()


