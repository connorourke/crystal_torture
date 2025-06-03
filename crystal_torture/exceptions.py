"""Custom exception classes for crystal_torture."""


class FortranNotAvailableError(ImportError):
	"""Raised when Fortran extensions are not available for tortuosity analysis.
	
	This typically occurs when the package was installed without Fortran compiler
	support or the compiled extensions failed to load. Users should use Python-only
	methods as alternatives.
	"""
	
	def __init__(self, message=None):
		if message is None:
			message = (
				"Fortran extensions are not available for accelerated tortuosity analysis. "
				"Use torture_py() instead of torture_fort() for Python-only analysis."
			)
		super().__init__(message)