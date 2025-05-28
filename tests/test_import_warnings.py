"""
Test that import-time warnings are handled properly.

Simple tests to verify:
1. Imports are silent when Fortran extensions are unavailable
2. Errors only appear when trying to use unavailable functionality
"""
import unittest
import warnings
from unittest.mock import patch


class TestImportWarnings(unittest.TestCase):
	"""Test that imports are silent when Fortran extensions are unavailable."""
	
	@patch('pathlib.Path.glob', return_value=[])
	def test_imports_are_silent_when_fortran_unavailable(self, mock_glob):
		"""Test that importing modules produces no warnings when Fortran is unavailable."""
		with warnings.catch_warnings(record=True) as warning_list:
			warnings.simplefilter("always")
			
			import crystal_torture.tort
			import crystal_torture.dist
			import crystal_torture.cluster
			
			# Should produce no warnings
			self.assertEqual(len(warning_list), 0,
						   f"Imports should be silent, got warnings: {[str(w.message) for w in warning_list]}")
	
	@patch('pathlib.Path.glob', return_value=[])
	def test_error_only_when_using_fortran_functionality(self, mock_glob):
		"""Test that errors only appear when trying to use unavailable Fortran functionality."""
		from crystal_torture.cluster import Cluster
		from crystal_torture.node import Node
		
		# Create minimal cluster
		node = Node(0, "Li", {"UC_index": "0", "Halo": False}, [])
		cluster = Cluster({node})
		
		# Should raise ImportError when trying to use Fortran functionality
		with self.assertRaises(ImportError):
			cluster.torture_fort()


if __name__ == "__main__":
	unittest.main()