"""Tests for the edges module."""

import unittest
import tempfile
import json
from pathlib import Path

from crystal_torture.edges import (
    Edge,
    EdgeData,
    load_edges,
    save_edges,
    edges_from_structure,
    edges_from_labels,
    graph_from_edges,
)
from pymatgen.core import Structure, Lattice


class TestEdge(unittest.TestCase):
    """Tests for Edge dataclass."""

    def test_edge_creation_with_weight(self):
        """Test Edge can be created with nodes and weight."""
        edge = Edge(nodes=(0, 1), weight=0.5)
        self.assertEqual(edge.nodes, (0, 1))
        self.assertEqual(edge.weight, 0.5)

    def test_edge_creation_without_weight(self):
        """Test Edge can be created with nodes only (weight defaults to None)."""
        edge = Edge(nodes=(0, 1))
        self.assertEqual(edge.nodes, (0, 1))
        self.assertIsNone(edge.weight)

    def test_edge_nodes_are_tuple(self):
        """Test that nodes are stored as a tuple."""
        edge = Edge(nodes=(2, 5), weight=0.3)
        self.assertIsInstance(edge.nodes, tuple)
        self.assertEqual(len(edge.nodes), 2)


class TestEdgeData(unittest.TestCase):
    """Tests for EdgeData dataclass."""

    def test_edge_data_creation(self):
        """Test EdgeData can be created with num_nodes and edges."""
        edges = [Edge(nodes=(0, 1), weight=0.5), Edge(nodes=(1, 2), weight=0.3)]
        edge_data = EdgeData(num_nodes=3, edges=edges)
        self.assertEqual(edge_data.num_nodes, 3)
        self.assertEqual(len(edge_data.edges), 2)

    def test_edge_data_weighted_property_true_when_edges_have_weights(self):
        """Test weighted property returns True when all edges have weights."""
        edges = [Edge(nodes=(0, 1), weight=0.5), Edge(nodes=(1, 2), weight=0.3)]
        edge_data = EdgeData(num_nodes=3, edges=edges)
        self.assertTrue(edge_data.weighted)

    def test_edge_data_weighted_property_false_when_edges_unweighted(self):
        """Test weighted property returns False when edges have no weights."""
        edges = [Edge(nodes=(0, 1)), Edge(nodes=(1, 2))]
        edge_data = EdgeData(num_nodes=3, edges=edges)
        self.assertFalse(edge_data.weighted)

    def test_edge_data_weighted_property_false_when_no_edges(self):
        """Test weighted property returns False when there are no edges."""
        edge_data = EdgeData(num_nodes=3, edges=[])
        self.assertFalse(edge_data.weighted)

    def test_edge_data_raises_error_on_mixed_weights(self):
        """Test EdgeData raises ValueError when some edges have weights and some don't."""
        edges = [Edge(nodes=(0, 1), weight=0.5), Edge(nodes=(1, 2))]
        with self.assertRaises(ValueError) as context:
            EdgeData(num_nodes=3, edges=edges)
        self.assertIn("inconsistent", str(context.exception).lower())

    def test_edge_data_raises_error_on_invalid_node_index(self):
        """Test EdgeData raises ValueError when edge references invalid node index."""
        edges = [Edge(nodes=(0, 5))]  # 5 is out of range for num_nodes=3
        with self.assertRaises(ValueError) as context:
            EdgeData(num_nodes=3, edges=edges)
        self.assertIn("index", str(context.exception).lower())

    def test_edge_data_raises_error_on_negative_node_index(self):
        """Test EdgeData raises ValueError when edge references negative node index."""
        edges = [Edge(nodes=(-1, 1))]
        with self.assertRaises(ValueError) as context:
            EdgeData(num_nodes=3, edges=edges)
        self.assertIn("index", str(context.exception).lower())

    def test_edge_data_raises_error_on_duplicate_edges(self):
        """Test EdgeData raises ValueError when duplicate edges exist."""
        edges = [Edge(nodes=(0, 1)), Edge(nodes=(0, 1))]
        with self.assertRaises(ValueError) as context:
            EdgeData(num_nodes=3, edges=edges)
        self.assertIn("duplicate", str(context.exception).lower())

    def test_edge_data_raises_error_on_non_canonical_ordering(self):
        """Test EdgeData raises ValueError when edge nodes are not canonically ordered."""
        edges = [Edge(nodes=(2, 1))]  # Should be (1, 2)
        with self.assertRaises(ValueError) as context:
            EdgeData(num_nodes=3, edges=edges)
        self.assertIn("canonical", str(context.exception).lower())

    def test_edge_data_raises_error_on_non_positive_num_nodes(self):
        """Test EdgeData raises ValueError when num_nodes is not positive."""
        with self.assertRaises(ValueError) as context:
            EdgeData(num_nodes=0, edges=[])
        self.assertIn("positive", str(context.exception).lower())


class TestEdgeDataFilter(unittest.TestCase):
    """Tests for EdgeData.filter() method."""

    def test_filter_returns_matching_edges(self):
        """Test filter returns edges where predicate is True."""
        edges = [
            Edge(nodes=(0, 1), weight=0.2),
            Edge(nodes=(0, 2), weight=0.5),
            Edge(nodes=(1, 2), weight=0.8),
        ]
        edge_data = EdgeData(num_nodes=3, edges=edges)
        filtered = edge_data.filter(lambda e: e.weight <= 0.5)
        self.assertEqual(len(filtered.edges), 2)
        weights = [e.weight for e in filtered.edges]
        self.assertIn(0.2, weights)
        self.assertIn(0.5, weights)

    def test_filter_returns_empty_edge_data_when_no_edges_match(self):
        """Test filter returns EdgeData with empty edge list when none match."""
        edges = [Edge(nodes=(0, 1), weight=0.8), Edge(nodes=(1, 2), weight=0.9)]
        edge_data = EdgeData(num_nodes=3, edges=edges)
        filtered = edge_data.filter(lambda e: e.weight < 0.5)
        self.assertEqual(len(filtered.edges), 0)

    def test_filter_preserves_num_nodes(self):
        """Test filter preserves num_nodes even when edges are removed."""
        edges = [Edge(nodes=(0, 1), weight=0.8)]
        edge_data = EdgeData(num_nodes=10, edges=edges)
        filtered = edge_data.filter(lambda e: e.weight < 0.5)
        self.assertEqual(filtered.num_nodes, 10)

    def test_filter_by_weight_threshold(self):
        """Test filtering by weight threshold."""
        edges = [
            Edge(nodes=(0, 1), weight=0.1),
            Edge(nodes=(0, 2), weight=0.3),
            Edge(nodes=(1, 2), weight=0.5),
            Edge(nodes=(0, 3), weight=0.7),
        ]
        edge_data = EdgeData(num_nodes=4, edges=edges)
        filtered = edge_data.filter(lambda e: 0.2 <= e.weight <= 0.6)
        self.assertEqual(len(filtered.edges), 2)

    def test_filter_by_node_membership(self):
        """Test filtering by node membership."""
        edges = [
            Edge(nodes=(0, 1)),
            Edge(nodes=(0, 2)),
            Edge(nodes=(1, 2)),
            Edge(nodes=(2, 3)),
        ]
        edge_data = EdgeData(num_nodes=4, edges=edges)
        # Filter for edges containing node 0
        filtered = edge_data.filter(lambda e: 0 in e.nodes)
        self.assertEqual(len(filtered.edges), 2)
        for edge in filtered.edges:
            self.assertIn(0, edge.nodes)

    def test_filter_returns_new_instance(self):
        """Test that filter returns a new EdgeData instance."""
        edges = [Edge(nodes=(0, 1), weight=0.5)]
        edge_data = EdgeData(num_nodes=3, edges=edges)
        filtered = edge_data.filter(lambda e: True)
        self.assertIsNot(filtered, edge_data)


class TestLoadEdges(unittest.TestCase):
    """Tests for load_edges function."""

    def test_load_edges_parses_valid_weighted_json(self):
        """Test load_edges correctly parses valid JSON file with weights."""
        data = {
            "num_nodes": 4,
            "edges": [
                {"nodes": [0, 1], "weight": 0.35},
                {"nodes": [1, 2], "weight": 0.52},
                {"nodes": [2, 3], "weight": 0.41},
            ],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(data, f)
            f.flush()
            edge_data = load_edges(f.name)

        self.assertEqual(edge_data.num_nodes, 4)
        self.assertEqual(len(edge_data.edges), 3)
        self.assertTrue(edge_data.weighted)
        self.assertEqual(edge_data.edges[0].nodes, (0, 1))
        self.assertEqual(edge_data.edges[0].weight, 0.35)

    def test_load_edges_parses_valid_unweighted_json(self):
        """Test load_edges correctly parses valid JSON file without weights."""
        data = {
            "num_nodes": 3,
            "edges": [
                {"nodes": [0, 1]},
                {"nodes": [0, 2]},
            ],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(data, f)
            f.flush()
            edge_data = load_edges(f.name)

        self.assertEqual(edge_data.num_nodes, 3)
        self.assertEqual(len(edge_data.edges), 2)
        self.assertFalse(edge_data.weighted)
        self.assertIsNone(edge_data.edges[0].weight)

    def test_load_edges_raises_error_on_mixed_weights(self):
        """Test load_edges raises ValueError when edges have inconsistent weights."""
        data = {
            "num_nodes": 3,
            "edges": [
                {"nodes": [0, 1], "weight": 0.5},
                {"nodes": [1, 2]},  # No weight
            ],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(data, f)
            f.flush()
            with self.assertRaises(ValueError) as context:
                load_edges(f.name)
            self.assertIn("inconsistent", str(context.exception).lower())

    def test_load_edges_raises_error_on_missing_num_nodes(self):
        """Test load_edges raises ValueError when num_nodes is missing."""
        data = {
            "edges": [{"nodes": [0, 1]}],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(data, f)
            f.flush()
            with self.assertRaises(ValueError) as context:
                load_edges(f.name)
            self.assertIn("num_nodes", str(context.exception).lower())

    def test_load_edges_raises_error_on_missing_edges(self):
        """Test load_edges raises ValueError when edges field is missing."""
        data = {
            "num_nodes": 3,
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(data, f)
            f.flush()
            with self.assertRaises(ValueError) as context:
                load_edges(f.name)
            self.assertIn("edges", str(context.exception).lower())

    def test_load_edges_raises_error_on_invalid_json(self):
        """Test load_edges raises error on invalid JSON."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("not valid json {")
            f.flush()
            with self.assertRaises(ValueError):
                load_edges(f.name)

    def test_load_edges_accepts_path_object(self):
        """Test load_edges accepts Path object as filename."""
        data = {
            "num_nodes": 2,
            "edges": [{"nodes": [0, 1]}],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(data, f)
            f.flush()
            edge_data = load_edges(Path(f.name))

        self.assertEqual(edge_data.num_nodes, 2)


class TestSaveEdges(unittest.TestCase):
    """Tests for save_edges function."""

    def test_save_edges_writes_weighted_json(self):
        """Test save_edges writes correct JSON for weighted edges."""
        edges = [
            Edge(nodes=(0, 1), weight=0.35),
            Edge(nodes=(1, 2), weight=0.52),
        ]
        edge_data = EdgeData(num_nodes=3, edges=edges)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            save_edges(edge_data, f.name)

        with open(f.name, "r") as f:
            data = json.load(f)

        self.assertEqual(data["num_nodes"], 3)
        self.assertEqual(len(data["edges"]), 2)
        self.assertEqual(data["edges"][0]["nodes"], [0, 1])
        self.assertEqual(data["edges"][0]["weight"], 0.35)

    def test_save_edges_writes_unweighted_json(self):
        """Test save_edges writes correct JSON for unweighted edges."""
        edges = [Edge(nodes=(0, 1)), Edge(nodes=(1, 2))]
        edge_data = EdgeData(num_nodes=3, edges=edges)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            save_edges(edge_data, f.name)

        with open(f.name, "r") as f:
            data = json.load(f)

        self.assertEqual(data["num_nodes"], 3)
        self.assertEqual(len(data["edges"]), 2)
        self.assertEqual(data["edges"][0]["nodes"], [0, 1])
        self.assertNotIn("weight", data["edges"][0])

    def test_save_load_round_trip_preserves_weighted_data(self):
        """Test that save/load round-trip preserves weighted edge data."""
        original_edges = [
            Edge(nodes=(0, 1), weight=0.35),
            Edge(nodes=(0, 2), weight=0.52),
            Edge(nodes=(1, 2), weight=0.41),
        ]
        original = EdgeData(num_nodes=3, edges=original_edges)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            save_edges(original, f.name)
            loaded = load_edges(f.name)

        self.assertEqual(loaded.num_nodes, original.num_nodes)
        self.assertEqual(len(loaded.edges), len(original.edges))
        for orig, load in zip(original.edges, loaded.edges):
            self.assertEqual(orig.nodes, load.nodes)
            self.assertEqual(orig.weight, load.weight)

    def test_save_load_round_trip_preserves_unweighted_data(self):
        """Test that save/load round-trip preserves unweighted edge data."""
        original_edges = [
            Edge(nodes=(0, 1)),
            Edge(nodes=(0, 2)),
            Edge(nodes=(1, 2)),
        ]
        original = EdgeData(num_nodes=3, edges=original_edges)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            save_edges(original, f.name)
            loaded = load_edges(f.name)

        self.assertEqual(loaded.num_nodes, original.num_nodes)
        self.assertEqual(len(loaded.edges), len(original.edges))
        for orig, load in zip(original.edges, loaded.edges):
            self.assertEqual(orig.nodes, load.nodes)
            self.assertIsNone(load.weight)

    def test_save_edges_accepts_path_object(self):
        """Test save_edges accepts Path object as filename."""
        edge_data = EdgeData(num_nodes=2, edges=[Edge(nodes=(0, 1))])

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            save_edges(edge_data, Path(f.name))

        with open(f.name, "r") as f:
            data = json.load(f)

        self.assertEqual(data["num_nodes"], 2)


# Get the directory containing this test file
TEST_DIR = Path(__file__).parent
STRUCTURE_FILES_DIR = TEST_DIR / "STRUCTURE_FILES"


class TestEdgesFromStructure(unittest.TestCase):
    """Tests for edges_from_structure function."""

    def setUp(self):
        """Create a simple test structure."""
        # Simple cubic lattice with 2 atoms close together
        lattice = Lattice.cubic(5.0)
        species = ["Li", "Li"]
        coords = [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0]]  # 2.5 Angstroms apart
        self.simple_structure = Structure(lattice, species, coords)

    def test_edges_from_structure_finds_neighbours_within_rcut(self):
        """Test that edges_from_structure finds neighbours within rcut."""
        edge_data = edges_from_structure(self.simple_structure, rcut=3.0)
        # The two atoms are 2.5 A apart, so should be connected
        self.assertEqual(edge_data.num_nodes, 2)
        self.assertEqual(len(edge_data.edges), 1)
        self.assertEqual(edge_data.edges[0].nodes, (0, 1))

    def test_edges_from_structure_no_edges_when_rcut_too_small(self):
        """Test that no edges are found when rcut is too small."""
        edge_data = edges_from_structure(self.simple_structure, rcut=2.0)
        # The two atoms are 2.5 A apart, so should not be connected
        self.assertEqual(edge_data.num_nodes, 2)
        self.assertEqual(len(edge_data.edges), 0)

    def test_edges_from_structure_unweighted_when_no_weight_fn(self):
        """Test that edges are unweighted when no weight_fn is provided."""
        edge_data = edges_from_structure(self.simple_structure, rcut=3.0)
        self.assertFalse(edge_data.weighted)
        for edge in edge_data.edges:
            self.assertIsNone(edge.weight)

    def test_edges_from_structure_applies_weight_fn(self):
        """Test that weight_fn is applied to edges."""
        # Weight is just the distance
        edge_data = edges_from_structure(
            self.simple_structure,
            rcut=3.0,
            weight_fn=lambda s1, s2, d: d,
        )
        self.assertTrue(edge_data.weighted)
        # Distance should be approximately 2.5
        self.assertAlmostEqual(edge_data.edges[0].weight, 2.5, places=5)

    def test_edges_from_structure_canonical_ordering(self):
        """Test that edges have canonical ordering (i < j)."""
        edge_data = edges_from_structure(self.simple_structure, rcut=3.0)
        for edge in edge_data.edges:
            self.assertLess(edge.nodes[0], edge.nodes[1])

    def test_edges_from_structure_no_duplicate_edges(self):
        """Test that there are no duplicate edges."""
        # Create structure with multiple neighbours
        lattice = Lattice.cubic(3.0)
        species = ["Li", "Li", "Li"]
        coords = [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [0.0, 0.5, 0.0]]
        structure = Structure(lattice, species, coords)

        edge_data = edges_from_structure(structure, rcut=2.0)

        # Check for duplicates
        seen = set()
        for edge in edge_data.edges:
            self.assertNotIn(edge.nodes, seen)
            seen.add(edge.nodes)

    def test_edges_from_structure_with_real_structure(self):
        """Test edges_from_structure with a real structure file."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp")
        )
        # Filter to just Li atoms for simplicity
        li_structure = structure.copy()
        li_structure.remove_species(
            [s for s in structure.symbol_set if s != "Li"]
        )

        edge_data = edges_from_structure(li_structure, rcut=4.0)

        self.assertEqual(edge_data.num_nodes, len(li_structure.sites))
        # Should have edges
        self.assertGreater(len(edge_data.edges), 0)


class TestEdgesFromLabels(unittest.TestCase):
    """Tests for edges_from_labels function."""

    def setUp(self):
        """Create a test structure with labels."""
        lattice = Lattice.cubic(5.0)
        species = ["Li", "Li", "Na"]
        coords = [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [0.0, 0.5, 0.0]]
        self.structure = Structure(
            lattice,
            species,
            coords,
            site_properties={"label": ["A", "A", "B"]},
        )

    def test_edges_from_labels_assigns_weights_by_label(self):
        """Test that weights are correctly assigned based on site labels."""
        label_weights = {
            ("A", "A"): 0.3,
            ("A", "B"): 0.5,
        }
        edge_data = edges_from_labels(
            self.structure, rcut=3.0, label_weights=label_weights
        )

        self.assertTrue(edge_data.weighted)
        # Check weights are assigned correctly
        for edge in edge_data.edges:
            i, j = edge.nodes
            label_i = self.structure.sites[i].properties["label"]
            label_j = self.structure.sites[j].properties["label"]
            # Get expected weight (try both orders)
            expected = label_weights.get(
                (label_i, label_j), label_weights.get((label_j, label_i))
            )
            self.assertEqual(edge.weight, expected)

    def test_edges_from_labels_handles_symmetric_lookup(self):
        """Test that label lookup works with symmetric key pairs."""
        # Only specify (A, B), not (B, A)
        label_weights = {
            ("A", "A"): 0.3,
            ("A", "B"): 0.5,
        }
        # This should work even though we might encounter (B, A) order
        edge_data = edges_from_labels(
            self.structure, rcut=3.0, label_weights=label_weights
        )
        # Should not raise and should have edges
        self.assertGreater(len(edge_data.edges), 0)

    def test_edges_from_labels_raises_keyerror_on_missing_pair(self):
        """Test that KeyError is raised for missing label pair."""
        # Don't include A-B pair
        label_weights = {("A", "A"): 0.3}
        with self.assertRaises(KeyError):
            edges_from_labels(
                self.structure, rcut=3.0, label_weights=label_weights
            )


class TestGraphFromEdges(unittest.TestCase):
    """Tests for graph_from_edges function."""

    def setUp(self):
        """Create test structure and edge data."""
        self.structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp")
        )
        # Filter to just Li atoms
        self.li_structure = self.structure.copy()
        self.li_structure.remove_species(
            [s for s in self.structure.symbol_set if s != "Li"]
        )

    def test_graph_from_edges_creates_valid_graph(self):
        """Test that graph_from_edges creates a valid Graph object."""
        # Generate edges from structure first
        edge_data = edges_from_structure(self.li_structure, rcut=4.0)
        graph = graph_from_edges(self.li_structure, edge_data)

        # Graph should have clusters
        self.assertIsNotNone(graph.clusters)
        self.assertGreater(len(graph.clusters), 0)

    def test_graph_from_edges_handles_empty_edge_list(self):
        """Test that graph_from_edges handles empty edge list."""
        edge_data = EdgeData(num_nodes=len(self.li_structure.sites), edges=[])
        graph = graph_from_edges(self.li_structure, edge_data)

        # Should still create a valid graph
        self.assertIsNotNone(graph.clusters)
        # Each node should be its own cluster
        self.assertEqual(
            len(graph.clusters), len(self.li_structure.sites)
        )

    def test_graph_from_edges_percolation_analysis_works(self):
        """Test that percolation analysis works on graph from edges."""
        edge_data = edges_from_structure(self.li_structure, rcut=4.0)
        graph = graph_from_edges(self.li_structure, edge_data)

        # Should be able to call percolation methods
        frac = graph.return_frac_percolating()
        self.assertIsInstance(frac, float)
        self.assertGreaterEqual(frac, 0.0)
        self.assertLessEqual(frac, 1.0)

    def test_graph_from_edges_torture_py_works(self):
        """Test that torture_py works on graph from edges."""
        edge_data = edges_from_structure(self.li_structure, rcut=4.0)
        graph = graph_from_edges(self.li_structure, edge_data)

        # Should be able to run tortuosity analysis
        graph.torture_py()

        # Check that tortuosity was calculated
        self.assertIsNotNone(graph.tortuosity)

    def test_graph_from_edges_validates_num_nodes(self):
        """Test that graph_from_edges validates num_nodes matches structure."""
        # Create edge data with wrong num_nodes
        edge_data = EdgeData(num_nodes=100, edges=[])
        with self.assertRaises(ValueError):
            graph_from_edges(self.li_structure, edge_data)

    def test_graph_from_edges_filtered_threshold_sweep(self):
        """Test threshold sweep with filtered edges."""
        # Generate weighted edges
        edge_data = edges_from_structure(
            self.li_structure,
            rcut=4.0,
            weight_fn=lambda s1, s2, d: d,
        )

        # Check percolation at different thresholds
        thresholds = [2.0, 3.0, 4.0, 5.0]
        percolation_fracs = []

        for threshold in thresholds:
            filtered = edge_data.filter(lambda e: e.weight <= threshold)
            graph = graph_from_edges(self.li_structure, filtered)
            frac = graph.return_frac_percolating()
            percolation_fracs.append(frac)

        # Percolation fraction should generally increase with threshold
        # (more edges means more connectivity)
        # At minimum, the last threshold should have >= first threshold
        self.assertGreaterEqual(percolation_fracs[-1], percolation_fracs[0])


if __name__ == "__main__":
    unittest.main()
