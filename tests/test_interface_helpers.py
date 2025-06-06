import unittest
from unittest.mock import Mock, patch
import numpy as np
from crystal_torture.pymatgen_interface import (
	_python_dist, _python_shift_index, map_index
)
from crystal_torture.cluster import Cluster
from crystal_torture.node import Node


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

if __name__ == "__main__":
	unittest.main()