import unittest
from unittest.mock import Mock, patch
from pymatgen.core import Structure, Lattice
from crystal_torture import Graph, Cluster, Node
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

	def test_clusters_from_structure_invalid_elements(self):
		"""Test that clusters_from_structure raises error for invalid elements."""
		# Create simple structure with Li
		lattice = Lattice.cubic(4.0)
		structure = Structure(lattice, ["Li"], [[0, 0, 0]])
		
		# Try to request elements not in structure
		with self.assertRaises(ValueError) as context:
			clusters_from_structure(structure, 4.0, {"Mg"})
		
		self.assertIn("not a subset", str(context.exception))

	def test_graph_from_structure_invalid_elements(self):
		"""Test that graph_from_structure raises error for invalid elements."""
		lattice = Lattice.cubic(4.0)
		structure = Structure(lattice, ["Li"], [[0, 0, 0]])
		
		with self.assertRaises(ValueError) as context:
			graph_from_structure(structure, 4.0, {"Mg"})
		
		self.assertIn("not a subset", str(context.exception))

	def test_set_site_labels_length_mismatch(self):
		"""Test that set_site_labels raises error for length mismatch."""
		lattice = Lattice.cubic(4.0)
		structure = Structure(lattice, ["Li", "Li"], [[0, 0, 0], [0.5, 0.5, 0.5]])
		
		# Try to set wrong number of labels
		with self.assertRaises(ValueError) as context:
			set_site_labels(structure, ["A"])  # 2 sites but only 1 label
		
		self.assertIn("must match number of sites", str(context.exception))

	def test_cluster_torture_fort_without_fortran(self):
		"""Test that torture_fort raises error when Fortran unavailable."""
		with patch('crystal_torture.cluster.tort', None):
			node = Mock(spec=Node)
			node.labels = {"UC_index": "0", "Halo": False}
			cluster = Cluster({node})
			
			with self.assertRaises(ImportError) as context:
				cluster.torture_fort()
			
			self.assertIn("Fortran extensions not available", str(context.exception))

	def test_return_index_node_basic(self):
		"""Test return_index_node returns correct node."""
		node1 = Mock(spec=Node)
		node1.index = 5
		node2 = Mock(spec=Node)
		node2.index = 10
		
		cluster = Cluster({node1, node2})
		result = cluster.return_index_node(5)
		
		self.assertEqual(result, node1)

	def test_cluster_merge_creates_union(self):
		"""Test that cluster merge creates union of nodes."""
		node1 = Mock(spec=Node)
		node2 = Mock(spec=Node)
		node3 = Mock(spec=Node)
		
		cluster1 = Cluster({node1, node2})
		cluster2 = Cluster({node2, node3})
		
		merged = cluster1.merge(cluster2)
		
		self.assertEqual(merged.nodes, {node1, node2, node3})

	def test_cluster_is_neighbour_with_shared_nodes(self):
		"""Test that clusters with shared nodes are neighbours."""
		shared_node = Mock(spec=Node)
		node1 = Mock(spec=Node)
		node2 = Mock(spec=Node)
		
		cluster1 = Cluster({shared_node, node1})
		cluster2 = Cluster({shared_node, node2})
		
		self.assertTrue(cluster1.is_neighbour(cluster2))

	def test_cluster_is_neighbour_without_shared_nodes(self):
		"""Test that clusters without shared nodes are not neighbours."""
		node1 = Mock(spec=Node)
		node2 = Mock(spec=Node)
		node3 = Mock(spec=Node)
		node4 = Mock(spec=Node)
		
		cluster1 = Cluster({node1, node2})
		cluster2 = Cluster({node3, node4})
		
		self.assertFalse(cluster1.is_neighbour(cluster2))


if __name__ == "__main__":
	unittest.main()