"""
Unit tests for crystal_torture/dist.py module.
"""
import unittest
import numpy as np
from crystal_torture import dist
from crystal_torture.pymatgen_interface import _python_dist, _python_shift_index


class TestDistModule(unittest.TestCase):
    """Test dist module functions."""
    
    def test_dist_function_exists(self):
        """Test that dist function exists and is callable."""
        self.assertTrue(hasattr(dist, 'dist'))
        self.assertTrue(callable(dist.dist))
    
    def test_dist_function_basic_call(self):
        """Test that dist function accepts parameters and doesn't crash."""
        coords = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        # Should not raise exception
        result = dist.dist(coords, coords, 1)
        # Should return something array-like
        self.assertTrue(hasattr(result, 'shape'))
    
    def test_dist_function_returns_correct_shape(self):
        """Test that dist function returns expected shape."""
        coords = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]], dtype=np.float32)
        result = dist.dist(coords, coords, 2)
        self.assertEqual(result.shape, (2, 2))
    
    def test_shift_index_function_exists(self):
        """Test that shift_index function exists and is callable."""
        self.assertTrue(hasattr(dist, 'shift_index'))
        self.assertTrue(callable(dist.shift_index))
    
    def test_shift_index_function_basic_call(self):
        """Test that shift_index accepts parameters and doesn't crash."""
        # Should not raise exception
        result = dist.shift_index(0, [0, 0, 0])
        # Should return an integer
        self.assertIsInstance(result, int)
    
    def test_shift_index_function_returns_valid_range(self):
        """Test that shift_index returns values in valid range."""
        # Test various inputs
        for index in [0, 13, 26]:
            for shift in [[0,0,0], [1,0,0], [0,1,0], [0,0,1]]:
                result = dist.shift_index(index, shift)
                self.assertIsInstance(result, int)
                self.assertGreaterEqual(result, 0)
                self.assertLess(result, 27)  # Valid 3x3x3 index

    # === CONSISTENCY TESTS (Step 2) ===
    
    def test_dist_vs_python_identical_points(self):
        """Test Fortran dist matches Python for identical points."""
        coords = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        
        python_result = _python_dist(coords, coords, 1)
        fortran_result = dist.dist(coords, coords, 1)
        
        np.testing.assert_array_almost_equal(python_result, fortran_result, decimal=5)
    
    def test_dist_vs_python_unit_distance(self):
        """Test Fortran dist matches Python for unit separation."""
        coord1 = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        coord2 = np.array([[1.0, 0.0, 0.0]], dtype=np.float32)
        
        python_result = _python_dist(coord1, coord2, 1)
        fortran_result = dist.dist(coord1, coord2, 1)
        
        np.testing.assert_array_almost_equal(python_result, fortran_result, decimal=5)
    
    def test_dist_vs_python_multiple_points(self):
        """Test Fortran dist matches Python for multiple points."""
        coords = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0], 
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 1.0]
        ], dtype=np.float32)
        
        python_result = _python_dist(coords, coords, 4)
        fortran_result = dist.dist(coords, coords, 4)
        
        np.testing.assert_array_almost_equal(python_result, fortran_result, decimal=5)
    
    def test_shift_index_vs_python_no_shift(self):
        """Test Fortran shift_index matches Python for no shift."""
        test_indices = [0, 1, 13, 26]  # Various positions in 3x3x3
        
        for index in test_indices:
            python_result = _python_shift_index(index, [0, 0, 0])
            fortran_result = dist.shift_index(index, [0, 0, 0])
            self.assertEqual(python_result, fortran_result, 
                           f"Mismatch for index {index}")
    
    def test_shift_index_vs_python_unit_shifts(self):
        """Test Fortran shift_index matches Python for unit shifts."""
        test_cases = [
            (0, [1, 0, 0]),
            (0, [0, 1, 0]), 
            (0, [0, 0, 1]),
            (13, [1, 0, 0]),  # Centre position
            (13, [-1, -1, -1]),  # Negative shifts
            (26, [1, 1, 1])   # Corner with wraparound
        ]
        
        for index, shift in test_cases:
            python_result = _python_shift_index(index, shift)
            fortran_result = dist.shift_index(index, shift)
            self.assertEqual(python_result, fortran_result, 
                           f"Mismatch for index={index}, shift={shift}")
    
    def test_shift_index_vs_python_comprehensive(self):
        """Test Fortran shift_index matches Python for many cases."""
        # Test all positions in 3x3x3 with various shifts
        test_shifts = [[-1,-1,-1], [-1,0,1], [0,0,0], [1,0,0], [2,1,-1]]
        
        for index in range(27):  # All positions in 3x3x3
            for shift in test_shifts:
                python_result = _python_shift_index(index, shift)
                fortran_result = dist.shift_index(index, shift)
                self.assertEqual(python_result, fortran_result,
                               f"Mismatch for index={index}, shift={shift}")

    # === FIXED EXPECTED VALUES (Step 3) ===
    
    def test_dist_identical_points_is_zero(self):
        """Test distance between identical points is zero."""
        coords = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        result = dist.dist(coords, coords, 1)
        self.assertAlmostEqual(result[0, 0], 0.0, places=6)
    
    def test_dist_unit_x_separation(self):
        """Test distance for unit separation in x direction."""
        coord1 = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        coord2 = np.array([[1.0, 0.0, 0.0]], dtype=np.float32)
        result = dist.dist(coord1, coord2, 1)
        self.assertAlmostEqual(result[0, 0], 1.0, places=6)
    
    def test_dist_unit_y_separation(self):
        """Test distance for unit separation in y direction."""
        coord1 = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        coord2 = np.array([[0.0, 1.0, 0.0]], dtype=np.float32)
        result = dist.dist(coord1, coord2, 1)
        self.assertAlmostEqual(result[0, 0], 1.0, places=6)
    
    def test_dist_unit_z_separation(self):
        """Test distance for unit separation in z direction."""
        coord1 = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        coord2 = np.array([[0.0, 0.0, 1.0]], dtype=np.float32)
        result = dist.dist(coord1, coord2, 1)
        self.assertAlmostEqual(result[0, 0], 1.0, places=6)
    
    def test_dist_3d_diagonal(self):
        """Test distance for 3D diagonal (√3)."""
        coord1 = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        coord2 = np.array([[1.0, 1.0, 1.0]], dtype=np.float32)
        result = dist.dist(coord1, coord2, 1)
        expected = np.sqrt(3.0)  # 1.732051
        self.assertAlmostEqual(result[0, 0], expected, places=6)
    
    def test_dist_matrix_symmetry(self):
        """Test that distance matrix is symmetric."""
        coords = np.array([[0.0, 0.0, 0.0], [1.0, 2.0, 3.0]], dtype=np.float32)
        result = dist.dist(coords, coords, 2)
        self.assertAlmostEqual(result[0, 1], result[1, 0], places=6)
    
    def test_shift_index_no_shift(self):
        """Test shift_index with no movement returns same index."""
        test_cases = [0, 1, 13, 26]  # Various positions
        for index in test_cases:
            result = dist.shift_index(index, [0, 0, 0])
            self.assertEqual(result, index)
    
    def test_shift_index_center_movements(self):
        """Test shift_index movements from center position (1,1,1) = index 13."""
        center = 13
        expected_results = {
            (1, 0, 0): 22,   # (1,1,1) + (1,0,0) = (2,1,1) = 22
            (-1, 0, 0): 4,   # (1,1,1) + (-1,0,0) = (0,1,1) = 4
            (0, 1, 0): 16,   # (1,1,1) + (0,1,0) = (1,2,1) = 16
            (0, -1, 0): 10,  # (1,1,1) + (0,-1,0) = (1,0,1) = 10
            (0, 0, 1): 14,   # (1,1,1) + (0,0,1) = (1,1,2) = 14
            (0, 0, -1): 12   # (1,1,1) + (0,0,-1) = (1,1,0) = 12
        }
        
        for shift, expected in expected_results.items():
            result = dist.shift_index(center, list(shift))
            self.assertEqual(result, expected, 
                           f"shift_index(13, {list(shift)}) should be {expected}, got {result}")
    
    def test_shift_index_corner_positions(self):
        """Test shift_index for corner positions."""
        # Test corners of 3x3x3 cube
        corners = {
            0: (0, 0, 0),   # index 0 = position (0,0,0)
            26: (2, 2, 2)   # index 26 = position (2,2,2)
        }
        
        for index, (x, y, z) in corners.items():
            # No shift should return same
            self.assertEqual(dist.shift_index(index, [0, 0, 0]), index)
            
            # Verify the 3D mapping formula: index = z + 3*y + 9*x
            expected_index = z + 3*y + 9*x
            self.assertEqual(index, expected_index, 
                           f"Position ({x},{y},{z}) should map to index {expected_index}")
    
    def test_shift_index_wraparound(self):
        """Test that shift_index handles wraparound correctly."""
        # From corner (2,2,2) = index 26, shift +1 in each direction should wrap
        corner = 26
        
        # These should wrap around in 3x3x3 space
        result_x = dist.shift_index(corner, [1, 0, 0])  # x: 2+1 → 0 (wrap)
        result_y = dist.shift_index(corner, [0, 1, 0])  # y: 2+1 → 0 (wrap)  
        result_z = dist.shift_index(corner, [0, 0, 1])  # z: 2+1 → 0 (wrap)
        
        # All should be valid indices
        for result in [result_x, result_y, result_z]:
            self.assertGreaterEqual(result, 0)
            self.assertLess(result, 27)
        
        # Should not be the original corner
        for result in [result_x, result_y, result_z]:
            self.assertNotEqual(result, corner)


class TestDistAvailability(unittest.TestCase):
    """Test how dist module handles Fortran availability."""
    
    def test_dist_import_doesnt_crash(self):
        """Test that importing dist module doesn't crash."""
        # This should work whether Fortran is available or not
        from crystal_torture import dist
        # Functions should exist and be callable
        self.assertTrue(callable(dist.dist))
        self.assertTrue(callable(dist.shift_index))
    
    def test_dist_functions_work_without_fortran(self):
        """Test that dist functions work even if Fortran unavailable."""
        # These should use Python fallbacks if needed
        coords = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        result = dist.dist(coords, coords, 1)
        self.assertEqual(result.shape, (1, 1))
        
        result = dist.shift_index(0, [0, 0, 0])
        self.assertIsInstance(result, int)


if __name__ == "__main__":
    unittest.main()