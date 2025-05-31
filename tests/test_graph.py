import unittest
import os
from unittest.mock import Mock, patch
from pathlib import Path
from pymatgen.core import Structure, Lattice
from crystal_torture import Cluster, Graph, Node, tort
from crystal_torture.pymatgen_interface import (
    graph_from_file, 
    clusters_from_file, 
    graph_from_structure
)
from ddt import ddt, data, unpack
import subprocess

# Get the directory containing this test file
TEST_DIR = Path(__file__).parent
STRUCTURE_FILES_DIR = TEST_DIR / "STRUCTURE_FILES"


@ddt
class GraphTestCase(unittest.TestCase):
    """ Test for Graph Class"""

    def setUp(self):

        self.labels = ["A", "B", "O", "A", "B", "O"]
        self.elements = ["Mg", "Al", "O", "Mg", "Al", "O"]
        self.node_ids = [0, 1, 2, 3, 4, 5]
        self.neighbours = [
            [1, 2, 3, 5],
            [0, 2, 4, 5],
            [1, 0, 4, 3],
            [0, 4, 5, 2],
            [1, 2, 3, 5],
            [4, 3, 0, 1],
        ]
        self.nodes = [
            Mock(
                spec=Node,
                index=i,
                element=e,
                labels=l,
                neighbours_ind=n,
                neigbours=None,
            )
            for i, e, l, n in zip(
                self.node_ids, self.elements, self.labels, self.neighbours
            )
        ]

        for node in self.nodes:
            node.neighbours = [self.nodes[n] for n in node.neighbours_ind]
            node.neighbours = set(node.neighbours)

        self.cluster = Cluster({self.nodes.pop()})
        self.graph = Graph({self.cluster})

    def wrap_minimal_clusters(self):
        return self.graph.minimal_clusters

    def test_graph_is_initialised(self):
        self.cluster.grow_cluster()
        graph = Graph({self.cluster})

        c_nodes = set([node.index for node in self.cluster.nodes])
        g_nodes = set([node.index for node in graph.clusters.pop().nodes])

        self.assertEqual(g_nodes, c_nodes)

    def test_output_clusters(self):
        graph = graph_from_file(
            filename=str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp"),
            rcut=4.0,
            elements={"Li"},
        )

        graph.output_clusters(fmt="poscar", periodic=True)
        subprocess.run(f"mv *CLUS* {STRUCTURE_FILES_DIR}/", shell=True)
        clusters = clusters_from_file(
            filename=str(STRUCTURE_FILES_DIR / "POSCAR_CLUS_0.vasp"),
            rcut=4.0,
            elements={"Li"},
        )

        c_nodes = set([node.index for node in clusters.pop().nodes])
        g_nodes = set([node.index for node in graph.clusters.pop().nodes])

        self.assertEqual(g_nodes, c_nodes)

    def test_output_clusters_cif(self):
        graph = graph_from_file(
            filename=str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp"),
            rcut=4.0,
            elements={"Li"},
        )

        graph.output_clusters(fmt="cif")
        subprocess.run(f"mv *CLUS* {STRUCTURE_FILES_DIR}/", shell=True)
        clusters = clusters_from_file(
            filename=str(STRUCTURE_FILES_DIR / "POSCAR_CLUS_0.cif"),
            rcut=4.0,
            elements={"Li"},
        )

        c_nodes = set([node.index for node in clusters.pop().nodes])
        g_nodes = set([node.index for node in graph.clusters.pop().nodes])

        self.assertEqual(g_nodes, c_nodes)

    @data(0.195, 0.482, 0.727)
    def test_return_frac_perc(self, value):

        filename = str(STRUCTURE_FILES_DIR / "PERC" / f"POSCAR_{value}.vasp")
        graph = graph_from_file(filename=filename, rcut=4.0, elements={"Mg"})
        graph.output_clusters(fmt="poscar")
        subprocess.run(f"mv *CLUS* {STRUCTURE_FILES_DIR}/", shell=True)
        self.assertEqual(value, round(graph.return_frac_percolating(), 3))

    @data("POSCAR_2_clusters.vasp")
    def test_no_minimal_before_torture(self, value):
        self.assertRaises(ValueError, self.wrap_minimal_clusters)
        
    def test_torture_small_periodic_structure(self):
        """Test that torture completes successfully on small periodic structures."""
        
        lattice = Lattice.cubic(4.0)
        coords = [[0.25, 0.5, 0.5], [0.75, 0.5, 0.5]]
        species = ["Li", "Li"]
        structure = Structure(lattice, species, coords)
        
        graph = graph_from_structure(structure, rcut=2.5, elements={"Li"})
        
        graph.torture()
        
        # Should have tortuosity values
        self.assertIsNotNone(graph.tortuosity)
        self.assertEqual(len(graph.tortuosity), 2)  # Two UC sites
        
        # Both sites should have tortuosity = 2 for this 1D periodic structure
        for uc_idx, tort_value in graph.tortuosity.items():
            self.assertEqual(tort_value, 2)
            
    def test_torture_py_small_periodic_structure(self):
        """Test that torture_py completes successfully on small periodic structures."""
        
        lattice = Lattice.cubic(4.0)
        coords = [[0.25, 0.5, 0.5], [0.75, 0.5, 0.5]]
        species = ["Li", "Li"]
        structure = Structure(lattice, species, coords)
        
        graph = graph_from_structure(structure, rcut=2.5, elements={"Li"})
        
        graph.torture_py()
        
        # Should have tortuosity values
        self.assertIsNotNone(graph.tortuosity)
        self.assertEqual(len(graph.tortuosity), 2)  # Two UC sites
        
        # Both sites should have tortuosity = 2 for this 1D periodic structure
        for uc_idx, tort_value in graph.tortuosity.items():
            self.assertEqual(tort_value, 2)


if __name__ == "__main__":
    unittest.main()