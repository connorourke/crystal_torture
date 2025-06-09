import unittest
from unittest.mock import Mock, patch
from pymatgen.core import Structure, Lattice
from crystal_torture.graph import Graph
from crystal_torture.cluster import Cluster
from crystal_torture.node import Node
from crystal_torture.pymatgen_interface import clusters_from_structure, graph_from_structure
from crystal_torture.pymatgen_doping import set_site_labels


class ErrorConditionsTestCase(unittest.TestCase):
	"""Test error conditions and edge cases."""

	def test_minimal_clusters_property_before_torture(self):
		"""Test that minimal_clusters property raises error before torture."""
		cluster = Mock(spec=Cluster)
		graph = Graph({cluster})
		
		with self.assertRaises(ValueError) as context:
			_ = graph.minimal_clusters
		
		self.assertIn("minimal_clusters is not set until", str(context.exception))

	def test_set_site_labels_length_mismatch(self):
		"""Test that set_site_labels raises error for length mismatch."""
		lattice = Lattice.cubic(4.0)
		structure = Structure(lattice, ["Li", "Li"], [[0, 0, 0], [0.5, 0.5, 0.5]])
		
		# Try to set wrong number of labels
		with self.assertRaises(ValueError) as context:
			set_site_labels(structure, ["A"])  # 2 sites but only 1 label
		
		self.assertIn("must match number of sites", str(context.exception))


if __name__ == "__main__":
	unittest.main()