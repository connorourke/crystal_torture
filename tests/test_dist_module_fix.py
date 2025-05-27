# tests/test_dist_module_fix.py
"""
TDD test for fixing the dist module import warning.
"""
import pytest
import warnings
from pathlib import Path


class TestDistModuleFix:
    """Test that dist module imports cleanly without warnings."""
    
    def test_dist_module_imports_without_warnings(self):
        """Test that importing dist module doesn't generate warnings."""
        
        # Capture warnings during import
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            
            try:
                from crystal_torture import dist
                
                # Check if any warnings were generated about dist
                dist_warnings = [w for w in warning_list 
                               if "dist module not available" in str(w.message)]
                
                assert len(dist_warnings) == 0, \
                    f"Should not have dist unavailable warnings, got: {[str(w.message) for w in dist_warnings]}"
                
                # dist should not be None
                assert dist is not None, "dist module should be available"
                
            except ImportError as e:
                pytest.fail(f"Should be able to import dist module: {e}")
    
    def test_dist_module_has_expected_functions(self):
        """Test that dist module has the expected Fortran functions."""
        try:
            from crystal_torture import dist
            
            # Check for key functions that should be available
            expected_functions = ['dist', 'shift_index']
            
            for func_name in expected_functions:
                assert hasattr(dist, func_name), \
                    f"dist module should have {func_name} function"
                
        except ImportError:
            pytest.skip("dist module not available - this is what we're trying to fix")
    
    def test_pymatgen_interface_no_warnings(self):
        """Test that importing pymatgen_interface doesn't show dist warnings."""
        
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            
            # Import the module that was showing warnings
            from crystal_torture.pymatgen_interface import get_all_neighbors_and_image
            
            # Check for dist-related warnings
            dist_warnings = [w for w in warning_list 
                           if "dist module not available" in str(w.message)]
            
            assert len(dist_warnings) == 0, \
                f"pymatgen_interface should not show dist warnings: {[str(w.message) for w in dist_warnings]}"
    
    def test_dist_functions_are_callable(self):
        """Test that dist functions can actually be called."""
        try:
            from crystal_torture import dist
            
            # Test basic dist function call
            import numpy as np
            
            # Create simple test coordinates
            coords1 = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
            coords2 = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
            
            try:
                # This should work without error
                result = dist.dist(coords1, coords2, 2)
                assert result is not None, "dist function should return results"
                assert hasattr(result, 'shape'), "dist should return array-like result"
                
            except Exception as e:
                pytest.fail(f"dist function should be callable: {e}")
                
        except ImportError:
            pytest.skip("dist module not available - this is what we're trying to fix")
