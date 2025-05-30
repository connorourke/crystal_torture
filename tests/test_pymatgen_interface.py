import unittest
from unittest.mock import Mock
from pathlib import Path
from crystal_torture import Node, Cluster, tort
from crystal_torture.pymatgen_interface import (
    nodes_from_structure,
    clusters_from_file,
    clusters_from_structure,
    graph_from_structure,
)
from pymatgen.core import Structure, Lattice
from copy import deepcopy

# Get the directory containing this test file
TEST_DIR = Path(__file__).parent
STRUCTURE_FILES_DIR = TEST_DIR / "STRUCTURE_FILES"


class PymatgenTestCase(unittest.TestCase):
    """ Test for interface with pymatgen"""

    def setUp(self):
        self.labels = ["Li"] * 8
        self.elements = ["Li"] * 8
        self.node_ids = list(range(9))
        self.neighbours_ind = [
            set([2, 3, 6, 7]),
            set([2, 3, 6, 7]),
            set([0, 1, 4, 5]),
            set([0, 1, 4, 5]),
            set([2, 3, 6, 7]),
            set([2, 3, 6, 7]),
            set([0, 1, 4, 5]),
            set([0, 1, 4, 5]),
        ]
        self.mock_nodes = [
            Mock(
                spec=Node,
                index=i,
                element=e,
                labels=l,
                neighbours_ind=n,
                neigbours=None,
            )
            for i, e, l, n in zip(
                self.node_ids, self.elements, self.labels, self.neighbours_ind
            )
        ]

        for node in self.mock_nodes:
            node.neighbours = [self.mock_nodes[n] for n in node.neighbours_ind]
            node.neighbours = set(node.neighbours)
        self.mock_nodes = set(self.mock_nodes)
        self.cluster = Cluster(set(self.mock_nodes))

    def test_nodes_from_file(self):

        structure = Structure.from_file(str(STRUCTURE_FILES_DIR / "POSCAR_UC.vasp"))
        nodes = nodes_from_structure(structure, 4.0, get_halo=False)
        mock_neigh_ind = set(
            [frozenset(node.neighbours_ind) for node in self.mock_nodes]
        )
        neigh_ind = set([frozenset(node.neighbours_ind) for node in nodes])

        self.assertEqual(mock_neigh_ind, neigh_ind)
        self.assertEqual(
            set([node.index for node in self.mock_nodes]),
            set([node.index for node in nodes]),
        )
        self.assertEqual(
            set([node.element for node in self.mock_nodes]),
            set([node.element for node in nodes]),
        )

        node = set()
        node.add(nodes.pop())
        cluster1 = Cluster(node)
        cluster1.grow_cluster()
        self.assertEqual(
            set([node.index for node in self.cluster.nodes]),
            set([node.index for node in cluster1.nodes]),
        )
        self.assertEqual(
            set([node.element for node in self.cluster.nodes]),
            set([node.element for node in cluster1.nodes]),
        )

    def test_clusters_from_file(self):

        clusters1 = clusters_from_file(
            filename=str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp"),
            rcut=4.0,
            elements={"Li"},
        )
        tort.tort_mod.tear_down()
        clusters2 = clusters_from_file(
            filename=str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp"),
            rcut=3.5,
            elements={"Li"},
        )
        tort.tort_mod.tear_down()

        self.assertEqual(len(clusters1), 1)
        self.assertEqual(len(clusters2), 2)

    def test_cluster_from_structure(self):

        clusters1 = clusters_from_file(
            filename=str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp"),
            rcut=4.0,
            elements={"Li"},
        )
        structure = Structure.from_file(str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp"))
        clusters2 = clusters_from_structure(structure, rcut=4.0, elements={"Li"})

        neigh_set_1 = set(
            [frozenset(node.neighbours_ind) for node in clusters1.pop().nodes]
        )
        neigh_set_2 = set(
            [frozenset(node.neighbours_ind) for node in clusters2.pop().nodes]
        )

        self.assertEqual(neigh_set_1, neigh_set_2)

    def test_graph_from_structure(self):
        clusters1 = clusters_from_file(
            filename=str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp"),
            rcut=4.0,
            elements={"Li"},
        )
        structure = Structure.from_file(str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp"))
        graph = graph_from_structure(structure, rcut=4.0, elements={"Li"})

        neigh_set_1 = set(
            [frozenset(node.neighbours_ind) for node in clusters1.pop().nodes]
        )
        neigh_set_2 = set(
            [frozenset(node.neighbours_ind) for node in graph.clusters.pop().nodes]
        )

        self.assertEqual(neigh_set_1, neigh_set_2)

    def test_cluster_periodic(self):

        clusters1 = clusters_from_file(
            filename=str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp"),
            rcut=4.0,
            elements={"Li"},
        )
        tort.tort_mod.tear_down()

        clusters2 = clusters_from_file(
            filename=str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp"),
            rcut=3.5,
            elements={"Li"},
        )
        tort.tort_mod.tear_down()

        self.assertEqual(clusters1.pop().periodic, 3)
        if clusters2.pop().periodic == 3:
            self.assertEqual(clusters2.pop().periodic, 0)
        else:
            self.assertEqual(clusters2.pop().periodic, 3)

    def test_periodic(self):

        clusters1 = clusters_from_file(
            filename=str(STRUCTURE_FILES_DIR / "POSCAR_periodic_1.vasp"),
            rcut=4.0,
            elements={"Li"},
        )
        clusters2 = clusters_from_file(
            filename=str(STRUCTURE_FILES_DIR / "POSCAR_periodic_2.vasp"),
            rcut=4.0,
            elements={"Li"},
        )
        clusters3 = clusters_from_file(
            filename=str(STRUCTURE_FILES_DIR / "POSCAR_periodic_3.vasp"),
            rcut=4.0,
            elements={"Li"},
        )

        self.assertEqual(clusters1.pop().periodic, 1)
        self.assertEqual(clusters2.pop().periodic, 2)
        self.assertEqual(clusters3.pop().periodic, 3)
        
    def test_nodes_from_structure_does_not_modify_input(self):
        """
        Test that nodes_from_structure does not modify the input structure.
        """
        
        # Create simple test structure
        lattice = Lattice.cubic(10.0)
        coords = [[0.5, 0.5, 0.5]]
        species = ["Li"]
        original_structure = Structure(lattice, species, coords)
        
        # Make a copy before calling the function
        structure_before = deepcopy(original_structure)
        
        # Call the function that should NOT modify the input
        nodes = nodes_from_structure(original_structure, rcut=2.0, get_halo=True)
        
        # Assert that the input structure is unchanged
        self.assertEqual(original_structure, structure_before,
                        "nodes_from_structure modified the input structure")
        
        # The function should still work and return nodes
        self.assertIsNotNone(nodes)
        self.assertGreater(len(nodes), 0)
        
    def test_python_shift_index_negative_index(self):
        """Test that Python fallback shift_index raises ValueError for negative indices."""
        from crystal_torture.pymatgen_interface import _python_shift_index
        
        with self.assertRaises(ValueError):
            _python_shift_index(-1, [0, 0, 0])
        
        with self.assertRaises(ValueError):
            _python_shift_index(-10, [0, 0, 0])
        
        with self.assertRaises(ValueError):
            _python_shift_index(-100, [1, 2, 3])
    
    def test_python_shift_index_large_index(self):
        """Test Python fallback shift_index with index >= 27 works correctly for supercells."""
        from crystal_torture.pymatgen_interface import _python_shift_index
        
        # Test second supercell (indices 27-53)
        result = _python_shift_index(27, [0, 0, 0])
        self.assertEqual(result, 27)
        
        # Test with shift in second supercell
        result = _python_shift_index(27, [1, 0, 0])
        self.assertEqual(result, 36)  # 27 + 9
        
        # Test a larger index
        result = _python_shift_index(100, [0, 0, 0])
        self.assertEqual(result, 100)
        
        # Test the actual pattern used in create_halo
        for base in [0, 1, 5, 10]:
            supercell_index = 27 * base
            result = _python_shift_index(supercell_index, [0, 0, 0])
            self.assertEqual(result, supercell_index)


if __name__ == "__main__":
    unittest.main()