"""Integration tests for the edges module.

These tests verify that the edges module works correctly with real crystal
structures and produces results consistent with the existing rcut-based approach.
"""

import unittest
import tempfile
from pathlib import Path

from pymatgen.core import Structure, Lattice

from crystal_torture.edges import (
    Edge,
    EdgeData,
    load_edges,
    save_edges,
    edges_from_structure,
    edges_from_labels,
    graph_from_edges,
)
from crystal_torture.pymatgen_interface import (
    graph_from_structure,
    filter_structure_by_species,
)
from crystal_torture import tort


# Path to test structure files
TEST_DIR = Path(__file__).parent.parent
STRUCTURE_FILES_DIR = TEST_DIR / "STRUCTURE_FILES"
PERC_DIR = STRUCTURE_FILES_DIR / "PERC"


class TestEdgesEquivalenceWithRcut(unittest.TestCase):
    """Test that edge-based graphs match rcut-based graphs."""

    def tearDown(self):
        """Clean up Fortran state after each test."""
        if tort.tort_mod is not None:
            tort.tort_mod.tear_down()

    def test_equivalence_poscar_2_clusters(self):
        """Test edge-based approach matches rcut-based for POSCAR_2_clusters."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp")
        )
        rcut = 4.0
        elements = {"Li"}

        # Rcut-based approach
        rcut_graph = graph_from_structure(structure, rcut, elements)
        rcut_frac = rcut_graph.return_frac_percolating()

        # Edge-based approach
        li_structure = filter_structure_by_species(structure, list(elements))
        edge_data = edges_from_structure(li_structure, rcut)
        edge_graph = graph_from_edges(li_structure, edge_data)
        edge_frac = edge_graph.return_frac_percolating()

        self.assertAlmostEqual(rcut_frac, edge_frac, places=10)

    def test_equivalence_poscar_uc(self):
        """Test edge-based approach matches rcut-based for POSCAR_UC."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_UC.vasp")
        )
        rcut = 3.5
        elements = {"Li"}

        # Rcut-based approach
        rcut_graph = graph_from_structure(structure, rcut, elements)
        rcut_frac = rcut_graph.return_frac_percolating()

        # Edge-based approach
        li_structure = filter_structure_by_species(structure, list(elements))
        edge_data = edges_from_structure(li_structure, rcut)
        edge_graph = graph_from_edges(li_structure, edge_data)
        edge_frac = edge_graph.return_frac_percolating()

        self.assertAlmostEqual(rcut_frac, edge_frac, places=10)

    def test_equivalence_multiple_rcuts(self):
        """Test equivalence holds across different rcut values."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp")
        )
        elements = {"Li"}
        li_structure = filter_structure_by_species(structure, list(elements))

        for rcut in [3.0, 3.5, 4.0, 4.5]:
            with self.subTest(rcut=rcut):
                # Rcut-based approach
                rcut_graph = graph_from_structure(structure, rcut, elements)
                rcut_frac = rcut_graph.return_frac_percolating()

                # Edge-based approach
                edge_data = edges_from_structure(li_structure, rcut)
                edge_graph = graph_from_edges(li_structure, edge_data)
                edge_frac = edge_graph.return_frac_percolating()

                self.assertAlmostEqual(
                    rcut_frac, edge_frac, places=10,
                    msg=f"Mismatch at rcut={rcut}"
                )


class TestPercolationThresholdSweep(unittest.TestCase):
    """Test percolation threshold sweep with weighted edges."""

    def tearDown(self):
        """Clean up Fortran state after each test."""
        if tort.tort_mod is not None:
            tort.tort_mod.tear_down()

    def test_threshold_sweep_increases_percolation(self):
        """Test that higher thresholds include more edges and more percolation."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp")
        )
        li_structure = filter_structure_by_species(structure, ["Li"])

        # Generate weighted edges (weight = sum of site indices / 10)
        def index_weight(s1, s2):
            i = li_structure.index(s1)
            j = li_structure.index(s2)
            return (i + j) / 10.0

        edge_data = edges_from_structure(
            li_structure,
            rcut=5.0,
            weight_fn=index_weight,
        )

        # Sweep thresholds based on index weights
        thresholds = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 5.0]
        results = []

        for threshold in thresholds:
            filtered = edge_data.filter(lambda e: e.weight <= threshold)
            graph = graph_from_edges(li_structure, filtered)
            frac = graph.return_frac_percolating()
            results.append((threshold, len(filtered.edges), frac))

        # Edge count should be monotonically increasing
        edge_counts = [r[1] for r in results]
        for i in range(1, len(edge_counts)):
            self.assertGreaterEqual(
                edge_counts[i], edge_counts[i - 1],
                f"Edge count decreased at threshold {thresholds[i]}"
            )

        # Percolation should be monotonically increasing (or stay same)
        percolation_fracs = [r[2] for r in results]
        for i in range(1, len(percolation_fracs)):
            self.assertGreaterEqual(
                percolation_fracs[i], percolation_fracs[i - 1],
                f"Percolation decreased at threshold {thresholds[i]}"
            )

    def test_below_and_above_percolation_threshold(self):
        """Test structure that doesn't percolate at low threshold but does at high."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp")
        )
        li_structure = filter_structure_by_species(structure, ["Li"])

        # Generate weighted edges (weight = sum of site indices / 10)
        def index_weight(s1, s2):
            i = li_structure.index(s1)
            j = li_structure.index(s2)
            return (i + j) / 10.0

        edge_data = edges_from_structure(
            li_structure,
            rcut=5.0,
            weight_fn=index_weight,
        )

        # Very low threshold - likely no percolation
        low_filtered = edge_data.filter(lambda e: e.weight <= 0.1)
        low_graph = graph_from_edges(li_structure, low_filtered)
        low_frac = low_graph.return_frac_percolating()

        # High threshold - all edges included
        high_filtered = edge_data.filter(lambda e: e.weight <= 100.0)
        high_graph = graph_from_edges(li_structure, high_filtered)
        high_frac = high_graph.return_frac_percolating()

        # High threshold should have >= percolation than low
        self.assertGreaterEqual(high_frac, low_frac)


class TestPeriodicityDetection(unittest.TestCase):
    """Test that graph_from_edges correctly detects periodicity."""

    def tearDown(self):
        """Clean up Fortran state after each test."""
        if tort.tort_mod is not None:
            tort.tort_mod.tear_down()

    def test_periodic_1d(self):
        """Test 1D periodic structure is detected correctly."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_periodic_1.vasp")
        )
        li_structure = filter_structure_by_species(structure, ["Li"])

        edge_data = edges_from_structure(li_structure, rcut=4.0)
        graph = graph_from_edges(li_structure, edge_data)

        # Check at least one cluster has periodicity = 1
        periodicities = [c.periodic for c in graph.clusters if c.periodic]
        self.assertIn(1, periodicities)

    def test_periodic_2d(self):
        """Test 2D periodic structure is detected correctly."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_periodic_2.vasp")
        )
        li_structure = filter_structure_by_species(structure, ["Li"])

        edge_data = edges_from_structure(li_structure, rcut=4.0)
        graph = graph_from_edges(li_structure, edge_data)

        # Check at least one cluster has periodicity = 2
        periodicities = [c.periodic for c in graph.clusters if c.periodic]
        self.assertIn(2, periodicities)

    def test_periodic_3d(self):
        """Test 3D periodic structure is detected correctly."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_periodic_3.vasp")
        )
        li_structure = filter_structure_by_species(structure, ["Li"])

        edge_data = edges_from_structure(li_structure, rcut=4.0)
        graph = graph_from_edges(li_structure, edge_data)

        # Check at least one cluster has periodicity = 3
        periodicities = [c.periodic for c in graph.clusters if c.periodic]
        self.assertIn(3, periodicities)


class TestTortuosityAnalysis(unittest.TestCase):
    """Test tortuosity analysis on edge-based graphs."""

    def tearDown(self):
        """Clean up Fortran state after each test."""
        if tort.tort_mod is not None:
            tort.tort_mod.tear_down()

    def test_torture_py_on_edge_graph(self):
        """Test Python tortuosity analysis works on edge-based graph."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp")
        )
        li_structure = filter_structure_by_species(structure, ["Li"])

        edge_data = edges_from_structure(li_structure, rcut=4.0)
        graph = graph_from_edges(li_structure, edge_data)

        # Run tortuosity analysis
        graph.torture_py()

        # Check tortuosity was calculated
        self.assertIsNotNone(graph.tortuosity)
        self.assertGreater(len(graph.tortuosity), 0)

        # Tortuosity values should be positive integers
        for site_idx, tort_val in graph.tortuosity.items():
            self.assertIsInstance(tort_val, (int, float))
            self.assertGreater(tort_val, 0)

    def test_torture_fort_on_edge_graph(self):
        """Test Fortran tortuosity analysis works on edge-based graph."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp")
        )
        li_structure = filter_structure_by_species(structure, ["Li"])

        edge_data = edges_from_structure(li_structure, rcut=4.0)
        graph = graph_from_edges(li_structure, edge_data)

        # Run tortuosity analysis (Fortran)
        graph.torture()

        # Check tortuosity was calculated
        self.assertIsNotNone(graph.tortuosity)
        self.assertGreater(len(graph.tortuosity), 0)

    def test_torture_py_matches_fort(self):
        """Test Python and Fortran tortuosity give same results."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp")
        )
        li_structure = filter_structure_by_species(structure, ["Li"])

        # Python torture
        edge_data_py = edges_from_structure(li_structure, rcut=4.0)
        graph_py = graph_from_edges(li_structure, edge_data_py)
        graph_py.torture_py()

        # Clean up before creating new graph
        if tort.tort_mod is not None:
            tort.tort_mod.tear_down()

        # Fortran torture
        edge_data_fort = edges_from_structure(li_structure, rcut=4.0)
        graph_fort = graph_from_edges(li_structure, edge_data_fort)
        graph_fort.torture()

        # Compare tortuosity values
        self.assertEqual(
            set(graph_py.tortuosity.keys()),
            set(graph_fort.tortuosity.keys())
        )
        for site_idx in graph_py.tortuosity:
            self.assertEqual(
                graph_py.tortuosity[site_idx],
                graph_fort.tortuosity[site_idx],
                f"Mismatch at site {site_idx}"
            )


class TestFullRoundTrip(unittest.TestCase):
    """Test full workflow: structure → edges → save → load → graph."""

    def tearDown(self):
        """Clean up Fortran state after each test."""
        if tort.tort_mod is not None:
            tort.tort_mod.tear_down()

    def test_round_trip_preserves_percolation(self):
        """Test save/load round-trip preserves percolation results."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp")
        )
        li_structure = filter_structure_by_species(structure, ["Li"])

        # Original workflow
        original_edges = edges_from_structure(li_structure, rcut=4.0)
        original_graph = graph_from_edges(li_structure, original_edges)
        original_frac = original_graph.return_frac_percolating()

        # Round-trip through file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            save_edges(original_edges, f.name)
            loaded_edges = load_edges(f.name)

        loaded_graph = graph_from_edges(li_structure, loaded_edges)
        loaded_frac = loaded_graph.return_frac_percolating()

        self.assertAlmostEqual(original_frac, loaded_frac, places=10)

    def test_round_trip_weighted_edges(self):
        """Test save/load round-trip preserves weighted edge data."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp")
        )
        li_structure = filter_structure_by_species(structure, ["Li"])

        # Original weighted edges (weight = constant)
        original_edges = edges_from_structure(
            li_structure,
            rcut=4.0,
            weight_fn=lambda s1, s2: 0.5,
        )

        # Round-trip
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            save_edges(original_edges, f.name)
            loaded_edges = load_edges(f.name)

        # Verify edge data matches
        self.assertEqual(loaded_edges.num_nodes, original_edges.num_nodes)
        self.assertEqual(len(loaded_edges.edges), len(original_edges.edges))
        self.assertTrue(loaded_edges.weighted)

        for orig, loaded in zip(original_edges.edges, loaded_edges.edges):
            self.assertEqual(orig.nodes, loaded.nodes)
            self.assertAlmostEqual(orig.weight, loaded.weight, places=10)

    def test_round_trip_filtered_edges(self):
        """Test round-trip with filtered edges produces same results."""
        structure = Structure.from_file(
            str(STRUCTURE_FILES_DIR / "POSCAR_2_clusters.vasp")
        )
        li_structure = filter_structure_by_species(structure, ["Li"])

        # Generate weighted edges (weight = sum of site indices / 10)
        def index_weight(s1, s2):
            i = li_structure.index(s1)
            j = li_structure.index(s2)
            return (i + j) / 10.0

        # Generate, filter, save
        full_edges = edges_from_structure(
            li_structure,
            rcut=5.0,
            weight_fn=index_weight,
        )
        filtered_edges = full_edges.filter(lambda e: e.weight <= 1.0)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            save_edges(filtered_edges, f.name)
            loaded_edges = load_edges(f.name)

        # Build graphs and compare
        filtered_graph = graph_from_edges(li_structure, filtered_edges)
        loaded_graph = graph_from_edges(li_structure, loaded_edges)

        self.assertAlmostEqual(
            filtered_graph.return_frac_percolating(),
            loaded_graph.return_frac_percolating(),
            places=10
        )


class TestLabelBasedWorkflow(unittest.TestCase):
    """Test label-based edge generation workflow."""

    def tearDown(self):
        """Clean up Fortran state after each test."""
        if tort.tort_mod is not None:
            tort.tort_mod.tear_down()

    def test_label_workflow_with_synthetic_structure(self):
        """Test label-based workflow with a synthetic labelled structure."""
        # Create a simple structure with labels
        lattice = Lattice.cubic(4.0)
        species = ["Li", "Li", "Li", "Li"]
        coords = [
            [0.0, 0.0, 0.0],
            [0.5, 0.0, 0.0],
            [0.0, 0.5, 0.0],
            [0.5, 0.5, 0.0],
        ]
        structure = Structure(
            lattice,
            species,
            coords,
            site_properties={"label": ["A", "B", "A", "B"]},
        )

        label_weights = {
            ("A", "A"): 0.1,  # Low weight - easy connection
            ("A", "B"): 0.5,  # Medium weight
            ("B", "B"): 0.9,  # High weight - difficult connection
        }

        edge_data = edges_from_labels(structure, rcut=3.0, label_weights=label_weights)

        # Should have weighted edges
        self.assertTrue(edge_data.weighted)

        # Filter and check
        low_threshold = edge_data.filter(lambda e: e.weight <= 0.2)
        high_threshold = edge_data.filter(lambda e: e.weight <= 1.0)

        # High threshold should include more edges
        self.assertGreaterEqual(len(high_threshold.edges), len(low_threshold.edges))

    def test_label_workflow_different_thresholds(self):
        """Test that different thresholds produce different connectivity."""
        lattice = Lattice.cubic(5.0)
        species = ["Li", "Li", "Li", "Na"]
        coords = [
            [0.0, 0.0, 0.0],
            [0.4, 0.0, 0.0],
            [0.0, 0.4, 0.0],
            [0.4, 0.4, 0.0],
        ]
        structure = Structure(
            lattice,
            species,
            coords,
            site_properties={"label": ["A", "A", "B", "B"]},
        )

        label_weights = {
            ("A", "A"): 0.2,
            ("A", "B"): 0.5,
            ("B", "B"): 0.8,
        }

        edge_data = edges_from_labels(structure, rcut=3.0, label_weights=label_weights)

        # Filter at different levels
        threshold_03 = edge_data.filter(lambda e: e.weight <= 0.3)
        threshold_06 = edge_data.filter(lambda e: e.weight <= 0.6)
        threshold_10 = edge_data.filter(lambda e: e.weight <= 1.0)

        # Check monotonic edge counts
        self.assertLessEqual(len(threshold_03.edges), len(threshold_06.edges))
        self.assertLessEqual(len(threshold_06.edges), len(threshold_10.edges))


class TestSyntheticStructures(unittest.TestCase):
    """Test with synthetic structures where behaviour is known a priori."""

    def tearDown(self):
        """Clean up Fortran state after each test."""
        if tort.tort_mod is not None:
            tort.tort_mod.tear_down()

    def test_1d_chain_percolates(self):
        """Test a 1D chain of atoms percolates in one dimension."""
        # Create a 1D chain along x-axis
        lattice = Lattice([[4.0, 0, 0], [0, 10, 0], [0, 0, 10]])
        species = ["Li", "Li"]
        coords = [[0.0, 0.5, 0.5], [0.5, 0.5, 0.5]]  # 2.0 A apart
        structure = Structure(lattice, species, coords)

        rcut = 2.5
        edge_data = edges_from_structure(structure, rcut=rcut)
        graph = graph_from_edges(structure, edge_data)

        # Should have one edge
        self.assertEqual(len(edge_data.edges), 1)

        # Should percolate (1D periodic)
        frac = graph.return_frac_percolating()
        self.assertEqual(frac, 1.0)

        # Check periodicity is 1D
        periodicities = [c.periodic for c in graph.clusters if c.periodic]
        self.assertEqual(max(periodicities), 1)

    def test_isolated_atoms_no_percolation(self):
        """Test isolated atoms (no edges) don't percolate."""
        # Create atoms far apart
        lattice = Lattice.cubic(20.0)
        species = ["Li", "Li"]
        coords = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]]  # ~17.3 A apart
        structure = Structure(lattice, species, coords)

        edge_data = edges_from_structure(structure, rcut=3.0)
        graph = graph_from_edges(structure, edge_data)

        # Should have no edges
        self.assertEqual(len(edge_data.edges), 0)

        # No percolation
        frac = graph.return_frac_percolating()
        self.assertEqual(frac, 0.0)

    def test_fully_connected_3d_percolates(self):
        """Test fully connected 3D structure percolates in 3D."""
        # Create a dense 3D arrangement
        lattice = Lattice.cubic(3.0)
        species = ["Li"] * 8
        coords = [
            [0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [0.0, 0.5, 0.0], [0.5, 0.5, 0.0],
            [0.0, 0.0, 0.5], [0.5, 0.0, 0.5], [0.0, 0.5, 0.5], [0.5, 0.5, 0.5],
        ]
        structure = Structure(lattice, species, coords)

        # Large rcut to ensure full connectivity
        edge_data = edges_from_structure(structure, rcut=3.0)
        graph = graph_from_edges(structure, edge_data)

        # Should have many edges
        self.assertGreater(len(edge_data.edges), 0)

        # Full percolation
        frac = graph.return_frac_percolating()
        self.assertEqual(frac, 1.0)

        # Should be 3D periodic
        periodicities = [c.periodic for c in graph.clusters if c.periodic]
        self.assertEqual(max(periodicities), 3)


class TestKnownPercolationFractions(unittest.TestCase):
    """Test against structures with known percolation fractions."""

    def tearDown(self):
        """Clean up Fortran state after each test."""
        if tort.tort_mod is not None:
            tort.tort_mod.tear_down()

    def test_known_frac_0195(self):
        """Test structure with known percolation fraction of 0.195."""
        structure = Structure.from_file(str(PERC_DIR / "POSCAR_0.195.vasp"))
        # These structures use Mg, not Li
        mg_structure = filter_structure_by_species(structure, ["Mg"])

        edge_data = edges_from_structure(mg_structure, rcut=4.0)
        graph = graph_from_edges(mg_structure, edge_data)
        frac = graph.return_frac_percolating()

        self.assertAlmostEqual(frac, 0.195, places=3)

    def test_known_frac_0482(self):
        """Test structure with known percolation fraction of 0.482."""
        structure = Structure.from_file(str(PERC_DIR / "POSCAR_0.482.vasp"))
        mg_structure = filter_structure_by_species(structure, ["Mg"])

        edge_data = edges_from_structure(mg_structure, rcut=4.0)
        graph = graph_from_edges(mg_structure, edge_data)
        frac = graph.return_frac_percolating()

        self.assertAlmostEqual(frac, 0.482, places=3)

    def test_known_frac_0727(self):
        """Test structure with known percolation fraction of 0.727."""
        structure = Structure.from_file(str(PERC_DIR / "POSCAR_0.727.vasp"))
        mg_structure = filter_structure_by_species(structure, ["Mg"])

        edge_data = edges_from_structure(mg_structure, rcut=4.0)
        graph = graph_from_edges(mg_structure, edge_data)
        frac = graph.return_frac_percolating()

        self.assertAlmostEqual(frac, 0.727, places=3)


if __name__ == "__main__":
    unittest.main()
