import unittest
from unittest.mock import Mock, patch
import numpy as np
from crystal_torture.pymatgen_interface import (
	_python_dist, _python_shift_index, map_index, set_cluster_periodic
)
from crystal_torture import Cluster, Node


class InterfaceHelpersTestCase(unittest.TestCase):
	"""Test for pymatgen_interface helper functions."""

	def test_python_dist_calculation(self):
		"""Test that Python distance calculation works correctly."""
		coord1 = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], dtype=np.float32)
		coord2 = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], dtype=np.float32)
		
		result = _python_dist(coord1, coord2, 2)
		
		# Should be 2x2 distance matrix
		self.assertEqual(result.shape, (2, 2))
		
		# Distance from point to itself should be 0
		self.assertAlmostEqual(result[0, 0], 0.0, places=6)
		self.assertAlmostEqual(result[1, 1], 0.0, places=6)
		
		# Distance between (0,0,0) and (1,0,0) should be 1
		self.assertAlmostEqual(result[0, 1], 1.0, places=6)
		self.assertAlmostEqual(result[1, 0], 1.0, places=6)

	def test_python_shift_index_no_shift(self):
		"""Test Python shift index with no shift."""
		result = _python_shift_index(0, [0, 0, 0])
		self.assertEqual(result, 0)

	def test_python_shift_index_with_shift(self):
		"""Test Python shift index with shift."""
		# Test basic shift
		result = _python_shift_index(0, [1, 0, 0])
		self.assertIsInstance(result, int)
		
		# Test another shift
		result = _python_shift_index(13, [0, 1, 0])  # Centre of 3x3x3
		self.assertIsInstance(result, int)

	def test_map_index_basic(self):
		"""Test map_index function with simple case."""
		uc_neighbours = [[1], [0]]  # Two nodes, each other's neighbour
		uc_index = [0, 27]  # UC indices for 3x3x3 supercell
		
		result = map_index(uc_neighbours, uc_index, 2, 2, 2)
		
		# Should return list of neighbour lists
		self.assertIsInstance(result, list)
		self.assertEqual(len(result), 16)  # 2 UC nodes * 2*2*2 supercell
		
		# Each sublist should contain neighbour indices
		for neighbours in result:
			self.assertIsInstance(neighbours, list)

	def test_set_cluster_periodic_3d(self):
		"""Test setting cluster periodicity for 3D periodic cluster."""
		# Create nodes with same UC_index appearing 27 times (3x3x3)
		nodes = set()
		for i in range(27):
			node = Mock(spec=Node)
			node.labels = {"UC_index": "0"}
			nodes.add(node)
		
		cluster = Mock(spec=Cluster)
		cluster.nodes = nodes
		cluster.return_key_nodes.return_value = nodes
		
		set_cluster_periodic(cluster)
		
		self.assertEqual(cluster.periodic, 3)

	def test_set_cluster_periodic_2d(self):
		"""Test setting cluster periodicity for 2D periodic cluster."""
		# Create 9 nodes (3x3 for 2D)
		nodes = set()
		for i in range(9):
			node = Mock(spec=Node)
			node.labels = {"UC_index": "0"}
			nodes.add(node)
		
		cluster = Mock(spec=Cluster)
		cluster.nodes = nodes
		cluster.return_key_nodes.return_value = nodes
		
		set_cluster_periodic(cluster)
		
		self.assertEqual(cluster.periodic, 2)

	def test_set_cluster_periodic_1d(self):
		"""Test setting cluster periodicity for 1D periodic cluster."""
		# Create 3 nodes for 1D
		nodes = set()
		for i in range(3):
			node = Mock(spec=Node)
			node.labels = {"UC_index": "0"}
			nodes.add(node)
		
		cluster = Mock(spec=Cluster)
		cluster.nodes = nodes
		cluster.return_key_nodes.return_value = nodes
		
		set_cluster_periodic(cluster)
		
		self.assertEqual(cluster.periodic, 1)

	def test_set_cluster_periodic_0d(self):
		"""Test setting cluster periodicity for non-periodic cluster."""
		# Create 1 node (non-periodic)
		node = Mock(spec=Node)
		node.labels = {"UC_index": "0"}
		nodes = {node}
		
		cluster = Mock(spec=Cluster)
		cluster.nodes = nodes
		cluster.return_key_nodes.return_value = nodes
		
		set_cluster_periodic(cluster)
		
		self.assertEqual(cluster.periodic, 0)


if __name__ == "__main__":
	unittest.main()