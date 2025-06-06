# tests/test_exceptions.py
"""Tests for custom exception classes."""
import unittest
from crystal_torture.exceptions import FortranNotAvailableError


class TestFortranNotAvailableError(unittest.TestCase):
	"""Test FortranNotAvailableError custom exception."""
	
	def test_fortran_not_available_error_exists(self):
		"""Test that FortranNotAvailableError can be imported from exceptions module."""
		from crystal_torture.exceptions import FortranNotAvailableError
		# Should import without error
		self.assertTrue(callable(FortranNotAvailableError))
	
	def test_fortran_not_available_error_inherits_from_import_error(self):
		"""Test that FortranNotAvailableError inherits from ImportError."""
		from crystal_torture.exceptions import FortranNotAvailableError
		
		error = FortranNotAvailableError()
		self.assertIsInstance(error, ImportError)
		self.assertTrue(issubclass(FortranNotAvailableError, ImportError))
	
	def test_fortran_not_available_error_has_helpful_default_message(self):
		"""Test that FortranNotAvailableError has a user-friendly default message."""
		from crystal_torture.exceptions import FortranNotAvailableError
		
		error = FortranNotAvailableError()
		message = str(error)
		
		# Should mention Fortran and suggest alternatives
		self.assertIn("Fortran", message)
		self.assertIn("not available", message.lower())
		# Should be user-friendly, not technical
		self.assertNotIn("allocate_nodes", message)
	
	def test_fortran_not_available_error_accepts_custom_message(self):
		"""Test that FortranNotAvailableError can accept custom messages."""
		from crystal_torture.exceptions import FortranNotAvailableError
		
		custom_message = "Custom error context for tortuosity analysis"
		error = FortranNotAvailableError(custom_message)
		
		self.assertEqual(str(error), custom_message)
	
	def test_fortran_not_available_error_importable_from_main_package(self):
		"""Test that FortranNotAvailableError can be imported from main crystal_torture package."""
		
		# Should be available at package level for easy user access
		error = FortranNotAvailableError()
		self.assertIsInstance(error, ImportError)


if __name__ == "__main__":
	unittest.main()