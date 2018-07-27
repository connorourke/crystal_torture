import unittest
import os
from unittest.mock import Mock
from pymatgen import Structure
from crystal_torture import Cluster, Graph, Node, tort
from crystal_torture.pymatgen_interface import graph_from_file, clusters_from_file
from ddt import ddt, data, unpack
import subprocess

@ddt
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
        graph = graph_from_file(filename="tests/STRUCTURE_FILES/POSCAR_2_clusters.vasp",rcut=4.0, elements={"Li"})
        tort.tort_mod.tear_down()

        clusters = clusters_from_file(filename="tests/STRUCTURE_FILES/POSCAR_2_clusters.vasp",rcut=4.0,elements={"Li"})
        tort.tort_mod.tear_down()
        c_nodes = set([node.index for node in clusters.pop().nodes])
        g_nodes = set([node.index for node in graph.clusters.pop().nodes])

        self.assertEqual( g_nodes,c_nodes)
            
    def test_output_clusters(self):
        graph = graph_from_file(filename="tests/STRUCTURE_FILES/POSCAR_2_clusters.vasp",rcut=4.0, elements={"Li"})
        
        graph.output_clusters(fmt='poscar',periodic=True)
        subprocess.run('mv *CLUS* tests/STRUCTURE_FILES/',shell=True)
        clusters = clusters_from_file(filename="tests/STRUCTURE_FILES/POSCAR_CLUS_0.vasp",rcut=4.0,elements={"Li"})
        
        c_nodes = set([node.index for node in clusters.pop().nodes])
        g_nodes = set([node.index for node in graph.clusters.pop().nodes])

        self.assertEqual( g_nodes,c_nodes)

    def test_output_clusters_cif(self):
        graph = graph_from_file(filename="tests/STRUCTURE_FILES/POSCAR_2_clusters.vasp",rcut=4.0, elements={"Li"})

        graph.output_clusters(fmt='cif')
        subprocess.run('mv *CLUS* tests/STRUCTURE_FILES/',shell=True)
        clusters = clusters_from_file(filename="tests/STRUCTURE_FILES/POSCAR_CLUS_0.cif",rcut=4.0,elements={"Li"})

        c_nodes = set([node.index for node in clusters.pop().nodes])
        g_nodes = set([node.index for node in graph.clusters.pop().nodes])

        self.assertEqual( g_nodes,c_nodes)

    @data(0.195,0.482,0.727)
    def test_return_frac_perc(self, value):

        filename="tests/STRUCTURE_FILES/PERC/POSCAR_"+str(value)+".vasp"
        graph = graph_from_file(filename=filename,rcut=4.0, elements={"Mg"})
        graph.output_clusters(fmt='poscar')
        subprocess.run('mv *CLUS* tests/STRUCTURE_FILES/',shell=True)
        self.assertEqual(value, round(graph.return_frac_percolating(),3))
        
if __name__ =='__main__':
    unittest.main()


