import unittest
from unittest.mock import Mock, patch
from pathlib import Path
from crystal_torture import Node, Cluster, tort
from crystal_torture.pymatgen_interface import (
    nodes_from_structure,
    clusters_from_file,
    clusters_from_structure,
    graph_from_structure,
    graph_from_file,
    filter_structure_by_species
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
        
    @patch('crystal_torture.pymatgen_interface.clusters_from_structure')
    @patch('crystal_torture.pymatgen_interface.Structure.from_file')
    def test_clusters_from_file_delegates_to_clusters_from_structure(
        self, mock_from_file, mock_clusters_from_structure
    ):
        """Test that clusters_from_file delegates to clusters_from_structure (target behaviour)."""
        mock_structure = Mock()
        mock_clusters = {Mock(), Mock()}
        mock_from_file.return_value = mock_structure
        mock_clusters_from_structure.return_value = mock_clusters
        
        filename = 'test.cif'
        rcut = 3.0
        elements = {'Li', 'O'}
        
        result = clusters_from_file(filename, rcut, elements)
        
        # Should load structure from file
        mock_from_file.assert_called_once_with(filename)
        
        # Should delegate to clusters_from_structure with loaded structure
        mock_clusters_from_structure.assert_called_once_with(
            structure=mock_structure,
            rcut=rcut,
            elements=elements
        )
        
        # Should return what clusters_from_structure returned
        self.assertEqual(result, mock_clusters)
        
    def test_clusters_from_structure_does_not_modify_input_structure(self):
        """Test that clusters_from_structure doesn't modify the input structure (target behaviour)."""
        from copy import deepcopy
        from pymatgen.core import Structure, Lattice
        
        lattice = Lattice.cubic(4.0)
        structure = Structure(lattice, ["Li", "Li", "O"], [[0, 0, 0], [0.5, 0.5, 0.5], [0.25, 0.25, 0.25]])
        original_structure = deepcopy(structure)
        
        # Mock downstream calls so we're only testing immutability
        with patch('crystal_torture.pymatgen_interface.nodes_from_structure'), \
             patch('crystal_torture.pymatgen_interface.set_fort_nodes'), \
             patch('crystal_torture.pymatgen_interface.Structure.from_sites'), \
             patch('crystal_torture.pymatgen_interface.set_cluster_periodic'):
             
            clusters_from_structure(structure, 3.0, {'Li'})
            
            self.assertEqual(structure, original_structure)

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
            
    # Add these test methods to the existing GraphTestCase class in test_graph.py:
    
    @patch('crystal_torture.pymatgen_interface.Graph')
    @patch('crystal_torture.pymatgen_interface.clusters_from_structure')
    def test_graph_from_structure_delegates_cleanly(
        self, mock_clusters_from_structure, mock_graph_class
    ):
        """Test that graph_from_structure delegates to clusters_from_structure without duplication."""
        # Arrange
        mock_structure = Mock()
        mock_clusters = Mock()
        mock_graph = Mock()
        mock_clusters_from_structure.return_value = mock_clusters
        mock_graph_class.return_value = mock_graph
        
        # Act
        result = graph_from_structure(mock_structure, 3.0, {'Li', 'O'})
        
        # Assert - should delegate cleanly without any processing
        mock_clusters_from_structure.assert_called_once_with(mock_structure, 3.0, {'Li', 'O'})
        mock_graph_class.assert_called_once_with(clusters=mock_clusters, structure=mock_structure)
        self.assertEqual(result, mock_graph)
    
    @patch('crystal_torture.pymatgen_interface.Graph')
    @patch('crystal_torture.pymatgen_interface.clusters_from_structure')
    def test_graph_from_structure_delegates_cleanly(
        self, mock_clusters_from_structure, mock_graph_class
    ):
        """Test that graph_from_structure delegates cluster creation and handles structure filtering."""
        # Arrange
        mock_structure = Mock()
        mock_structure.symbol_set = {'Li', 'O', 'P'}  # Make it iterable for legitimate filtering
        mock_clusters = Mock()
        mock_graph = Mock()
        mock_clusters_from_structure.return_value = mock_clusters
        mock_graph_class.return_value = mock_graph
        
        # Act
        result = graph_from_structure(mock_structure, 3.0, {'Li', 'O'})
        
        # Assert - should delegate cluster creation (the expensive part)
        mock_clusters_from_structure.assert_called_once_with(mock_structure, 3.0, {'Li', 'O'})
        # Graph creation with filtered structure is legitimate
        mock_graph_class.assert_called_once()
        self.assertEqual(result, mock_graph)
        
    def test_filter_structure_by_species_does_not_modify_original(self):
        """Test that filter_structure_by_species doesn't modify the input structure."""
        lattice = Lattice.cubic(4.0)
        structure = Structure(lattice, ["Li", "Mg"], [[0, 0, 0], [0.5, 0.5, 0.5]])
        structure_before = deepcopy(structure)
        filtered_structure = filter_structure_by_species(structure, ["Li"])
        self.assertEqual(structure, structure_before)
        
    def test_filter_structure_by_species_basic_filtering(self):
        """Test that filter_structure_by_species returns structure with only specified species."""
        lattice = Lattice.cubic(4.0)
        structure = Structure(lattice, ["Li", "Mg"], [[0, 0, 0], [0.5, 0.5, 0.5]])
        
        filtered_structure = filter_structure_by_species(structure, ["Li"])
        
        self.assertIsInstance(filtered_structure, Structure)
        self.assertEqual(set(filtered_structure.symbol_set), {"Li"})
        self.assertEqual(len(filtered_structure), 1)  # Should have 1 Li site
        
    def test_filter_structure_by_species_empty_list_raises_error(self):
        """Test that empty species_list raises ValueError."""
        lattice = Lattice.cubic(4.0)
        structure = Structure(lattice, ["Li"], [[0, 0, 0]])
        
        with self.assertRaises(ValueError):
            filter_structure_by_species(structure, [])
    
    def test_filter_structure_by_species_invalid_species_raises_error(self):
        """Test that species_list with elements not in structure raises ValueError."""
        lattice = Lattice.cubic(4.0)
        structure = Structure(lattice, ["Li"], [[0, 0, 0]])
        
        with self.assertRaises(ValueError):
            filter_structure_by_species(structure, ["Mg"])  # Mg not in structure
            
    def test_clusters_from_structure_integration_before_refactoring(self):
        """Integration test for clusters_from_structure before refactoring (temporary test)."""
        lattice = Lattice.cubic(4.0)
        structure = Structure(
            lattice, 
            ["Li", "Li", "Mg"], 
            [[0, 0, 0], [0.5, 0, 0], [0, 0.5, 0]]
        )
        original_structure = deepcopy(structure)
        
        clusters = clusters_from_structure(structure, rcut=4.0, elements={"Li"})
        
        # Test return type and basic properties
        self.assertIsInstance(clusters, set)
        self.assertGreater(len(clusters), 0)
        
        # Test that clusters contain only the requested elements
        for cluster in clusters:
            cluster_elements = {node.element for node in cluster.nodes}
            self.assertEqual(cluster_elements, {"Li"})
        
        # Test that original structure is not modified (will fail with current implementation)
        self.assertEqual(structure, original_structure)
        
        # Clean up Fortran state
        tort.tort_mod.tear_down()
        
    def test_clusters_from_structure_basic_functionality(self):
        """Test clusters_from_structure basic functionality."""
        # Simple structure: 2 Li atoms close enough to connect
        lattice = Lattice.cubic(4.0)
        structure = Structure(lattice, ["Li", "Li"], [[0, 0, 0], [1.0, 0, 0]])
        original_structure = deepcopy(structure)
        
        clusters = clusters_from_structure(structure, rcut=2.0, elements={"Li"})
        
        # Should return set
        self.assertIsInstance(clusters, set)
        
        # All clusters should contain only Li
        for cluster in clusters:
            for node in cluster.nodes:
                self.assertEqual(node.element, "Li")
        
        # Original structure should be unmodified
        self.assertEqual(structure, original_structure)
    
    # Clean up
    tort.tort_mod.tear_down()


if __name__ == "__main__":
    unittest.main()