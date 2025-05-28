import unittest
from unittest.mock import Mock
from pymatgen.core import Structure, Lattice
from crystal_torture import Graph, Cluster, Node


class GraphHelpersTestCase(unittest.TestCase):
	"""Test for Graph helper methods."""

	def setUp(self):
		# Create mock nodes with tortuosity data
		self.node1 = Mock(spec=Node)
		self.node1.labels = {"UC_index": "0", "Halo": False}
		self.node1.tortuosity = 2.0
		
		self.node2 = Mock(spec=Node)
		self.node2.labels = {"UC_index": "1", "Halo": False}
		self.node2.tortuosity = 3.0
		
		self.node3 = Mock(spec=Node)
		self.node3.labels = {"UC_index": "0", "Halo": True}
		self.node3.tortuosity = None
		
		# Create mock cluster
		self.cluster = Mock(spec=Cluster)
		self.cluster.return_key_nodes.return_value = {self.node1, self.node2}
		
		# Create minimal structure
		lattice = Lattice.cubic(4.0)
		self.structure = Structure(lattice, ["Li", "Li"], [[0, 0, 0], [0.5, 0.5, 0.5]])
		
		self.graph = Graph({self.cluster}, self.structure)

	def test_set_site_tortuosity(self):
		"""Test that site tortuosity is set correctly."""
		self.graph.set_site_tortuosity()
		
		expected_tortuosity = {"0": 2.0, "1": 3.0}
		self.assertEqual(self.graph.tortuosity, expected_tortuosity)

	def test_return_periodic_structure_no_structure_raises_error(self):
		"""Test that return_periodic_structure raises error when no structure."""
		# Create properly configured mock cluster
		mock_cluster = Mock(spec=Cluster)
		mock_cluster.periodic = 3  # Make it periodic so it gets processed
		mock_cluster.nodes = {self.node1}  # Add required nodes attribute
		
		graph_no_structure = Graph({mock_cluster}, None)
		
		with self.assertRaises(ValueError) as context:
			graph_no_structure.return_periodic_structure("poscar")
		
		self.assertIn("Structure is required", str(context.exception))

	def test_output_clusters_no_structure_raises_error(self):
		"""Test that output_clusters raises error when no structure."""
		# Create properly configured mock cluster  
		mock_cluster = Mock(spec=Cluster)
		mock_cluster.periodic = None  # Can be any value for this test
		mock_cluster.nodes = {self.node1}  # Add required nodes attribute
		
		graph_no_structure = Graph({mock_cluster}, None)
		
		with self.assertRaises(ValueError) as context:
			graph_no_structure.output_clusters("poscar")
		
		self.assertIn("Structure is required", str(context.exception))

	def test_return_frac_percolating_empty_clusters(self):
		"""Test fraction percolating calculation with empty clusters."""
		empty_cluster = Mock(spec=Cluster)
		empty_cluster.return_key_nodes.return_value = set()
		empty_cluster.periodic = 0
		
		graph = Graph({empty_cluster}, self.structure)
		result = graph.return_frac_percolating()
		
		self.assertEqual(result, 0.0)


if __name__ == "__main__":
	unittest.main()