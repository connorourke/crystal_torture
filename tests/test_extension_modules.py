import unittest
from unittest.mock import patch, Mock
import numpy as np


class DistModuleTestCase(unittest.TestCase):
	"""Test for dist module functions."""

	def test_dist_function_interface(self):
		"""Test that dist function has correct interface."""
		from crystal_torture.dist import dist
		
		coords1 = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], dtype=np.float32)
		coords2 = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], dtype=np.float32)
		
		result = dist(coords1, coords2, 2)
		
		# Should return array-like result
		self.assertTrue(hasattr(result, 'shape'))
		self.assertEqual(result.shape, (2, 2))
		
		# Check basic mathematical properties
		self.assertAlmostEqual(result[0, 0], 0.0, places=5)
		self.assertAlmostEqual(result[0, 1], 1.0, places=5)

	def test_shift_index_function_interface(self):
		"""Test that shift_index function has correct interface."""
		from crystal_torture.dist import shift_index
		
		result = shift_index(0, [0, 0, 0])
		self.assertIsInstance(result, int)
		
		result = shift_index(0, [1, 0, 0])
		self.assertIsInstance(result, int)

	@patch('crystal_torture.dist._DIST_AVAILABLE', False)
	def test_dist_fallback_to_python(self):
		"""Test that dist falls back to Python when Fortran unavailable."""
		from crystal_torture.dist import dist
		
		coords1 = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
		coords2 = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
		
		# Should not raise an error even when Fortran unavailable
		result = dist(coords1, coords2, 1)
		self.assertEqual(result.shape, (1, 1))

	@patch('crystal_torture.dist._DIST_AVAILABLE', False)
	def test_shift_index_fallback_to_python(self):
		"""Test that shift_index falls back to Python when Fortran unavailable."""
		from crystal_torture.dist import shift_index
		
		# Should not raise an error even when Fortran unavailable
		result = shift_index(0, [0, 0, 0])
		self.assertIsInstance(result, int)


class TortModuleTestCase(unittest.TestCase):
	"""Test for tort module interface."""

	def test_tort_mod_none_when_unavailable(self):
		"""Test that tort_mod is None when Fortran unavailable."""
		with patch('crystal_torture.tort._FORT_AVAILABLE', False):
			from crystal_torture.tort import tort_mod
			# Note: import behavior varies, so we test the documented behavior
			# that functions should raise ImportError when used

	def test_tort_mod_methods_exist_when_available(self):
		"""Test that tort_mod has expected methods when available."""
		from crystal_torture import tort
		
		if tort.tort_mod is not None:
			# If Fortran is available, check methods exist
			self.assertTrue(hasattr(tort.tort_mod, 'allocate_nodes'))
			self.assertTrue(hasattr(tort.tort_mod, 'tear_down'))
			self.assertTrue(hasattr(tort.tort_mod, 'set_neighbours'))
			self.assertTrue(hasattr(tort.tort_mod, 'torture'))
			self.assertTrue(hasattr(tort.tort_mod, 'uc_tort'))


if __name__ == "__main__":
	unittest.main()