"""
Unit tests for crystal_torture/tort.py module.
"""
import unittest
from unittest.mock import patch
from crystal_torture import tort
from crystal_torture.node import Node
from crystal_torture.cluster import Cluster
from crystal_torture.pymatgen_interface import set_fort_nodes
from crystal_torture.exceptions import FortranNotAvailableError


class TestTortModule(unittest.TestCase):
    """Test tort module functions."""
    
    def tearDown(self):
        """Clean up after each test."""
        if tort.tort_mod is not None:
            try:
                tort.tort_mod.tear_down()
            except:
                pass  # Ignore cleanup errors
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_allocate_nodes_exists(self):
        """Test that allocate_nodes function exists and is callable."""
        self.assertTrue(hasattr(tort.tort_mod, 'allocate_nodes'))
        self.assertTrue(callable(tort.tort_mod.allocate_nodes))
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_allocate_nodes_basic_call(self):
        """Test that allocate_nodes accepts parameters and doesn't crash."""
        # Should not raise exception
        tort.tort_mod.allocate_nodes(2, 1)
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_uc_tort_returns_list(self):
        """Test that uc_tort property returns a list."""
        tort.tort_mod.allocate_nodes(4, 2)
        result = tort.tort_mod.uc_tort
        self.assertIsInstance(result, list)
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_set_neighbours_exists(self):
        """Test that set_neighbours function exists and is callable."""
        self.assertTrue(hasattr(tort.tort_mod, 'set_neighbours'))
        self.assertTrue(callable(tort.tort_mod.set_neighbours))
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_set_neighbours_basic_call(self):
        """Test that set_neighbours accepts parameters and doesn't crash."""
        tort.tort_mod.allocate_nodes(4, 2)
        # Should not raise exception
        tort.tort_mod.set_neighbours(0, 0, 1, [1])
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_torture_exists(self):
        """Test that torture function exists and is callable."""
        self.assertTrue(hasattr(tort.tort_mod, 'torture'))
        self.assertTrue(callable(tort.tort_mod.torture))
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_torture_basic_call(self):
        """Test that torture accepts parameters and doesn't crash."""
        tort.tort_mod.allocate_nodes(2, 1)
        tort.tort_mod.set_neighbours(0, 0, 1, [1])
        tort.tort_mod.set_neighbours(1, 0, 1, [0])
        # Should not raise exception
        tort.tort_mod.torture(1, [0])
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_tear_down_exists(self):
        """Test that tear_down function exists and is callable."""
        self.assertTrue(hasattr(tort.tort_mod, 'tear_down'))
        self.assertTrue(callable(tort.tort_mod.tear_down))
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_tear_down_basic_call(self):
        """Test that tear_down doesn't crash."""
        tort.tort_mod.allocate_nodes(2, 1)
        # Should not raise exception
        tort.tort_mod.tear_down()
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_torture_vs_python_simple_case(self):
        """Test that Fortran and Python torture give same results."""
        # Create simple test case: 2-node system where nodes are neighbours
        node0 = Node(
            index=0,
            element="Li",
            uc_index=0,
            is_halo=False,
            neighbours_ind=[1]
        )
        node1 = Node(
            index=1,
            element="Li",
            uc_index=0,
            is_halo=True,
            neighbours_ind=[0]
        )
        
        # Set up neighbour relationships
        node0.neighbours = {node1}
        node1.neighbours = {node0}
        
        set_fort_nodes({node0, node1})
        
        # Test Python version
        cluster_py = Cluster({node0, node1})
        cluster_py.torture_py()
        python_result = node0.tortuosity
        
        # Reset for Fortran test
        node0.tortuosity = None
        
        # Test Fortran version
        cluster_fort = Cluster({node0, node1})
        cluster_fort.torture_fort()
        fortran_result = node0.tortuosity
        
        # Should give same result
        self.assertEqual(python_result, fortran_result)
        self.assertIsNotNone(python_result)
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_torture_vs_python_disconnected_case(self):
        """Test Python vs Fortran on disconnected nodes."""
        # Create 4-node system: two disconnected pairs
        nodes = []
        for i in range(4):
            uc_index = i // 2  # nodes 0,1 have UC_index="0", nodes 2,3 have UC_index="1"
            is_halo = (i % 2 == 1)  # nodes 1,3 are halo nodes
            
            node = Node(
                index=i,
                element="Li",
                uc_index=uc_index,
                is_halo=is_halo,
                neighbours_ind=[1-i if i < 2 else 5-i]  # 0↔1, 2↔3
            )
            nodes.append(node)
        
        # Set up neighbour relationships
        nodes[0].neighbours = {nodes[1]}
        nodes[1].neighbours = {nodes[0]}
        nodes[2].neighbours = {nodes[3]}
        nodes[3].neighbours = {nodes[2]}
        
        set_fort_nodes(set(nodes))
        
        # Test Python version
        cluster_py = Cluster(set(nodes))
        cluster_py.torture_py()
        python_results = [node.tortuosity for node in nodes if not node.is_halo]
        
        # Reset for Fortran test
        for node in nodes:
            node.tortuosity = None
        
        # Test Fortran version
        cluster_fort = Cluster(set(nodes))
        cluster_fort.torture_fort()
        fortran_results = [node.tortuosity for node in nodes if not node.is_halo]
        
        # Should give same results
        self.assertEqual(python_results, fortran_results)
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_allocate_nodes_array_size(self):
        """Test that allocate_nodes creates correctly sized array."""
        # Array size should be 2 * n2 (second parameter)
        test_cases = [(4, 2), (6, 3), (10, 5)]
        
        for n, n2 in test_cases:
            tort.tort_mod.allocate_nodes(n, n2)
            result = tort.tort_mod.uc_tort
            expected_size = 2 * n2
            self.assertEqual(len(result), expected_size, 
                           f"allocate_nodes({n}, {n2}) should create array of size {expected_size}")
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_allocate_nodes_initialization(self):
        """Test that uc_tort array is initialized to zeros."""
        tort.tort_mod.allocate_nodes(6, 3)
        result = tort.tort_mod.uc_tort
        expected = [0] * 6  # Should be all zeros
        self.assertEqual(result, expected)
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_simple_two_node_tortuosity(self):
        """Test tortuosity calculation for simple 2-node case with known result."""
        # Create simplest possible case: 2 nodes directly connected
        # Node 0 (UC_index=0, Halo=False) connects to Node 1 (UC_index=0, Halo=True)
        # Expected tortuosity: 1 (one edge to reach periodic image)
        
        node0 = Node(
            index=0,
            element="Li",
            uc_index=0,
            is_halo=False,
            neighbours_ind=[1]
        )
        node1 = Node(
            index=1,
            element="Li",
            uc_index=0,
            is_halo=True,
            neighbours_ind=[0]
        )
        
        node0.neighbours = {node1}
        node1.neighbours = {node0}
        
        set_fort_nodes({node0, node1})
        
        cluster = Cluster({node0, node1})
        cluster.torture_fort()
        
        # Should find periodic image in 1 step, so tortuosity = 1
        self.assertEqual(node0.tortuosity, 1)
        self.assertIsNone(node1.tortuosity)  # Halo nodes don't get tortuosity calculated
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_tear_down_clears_state(self):
        """Test that tear_down properly clears allocated state."""
        # Allocate some nodes
        tort.tort_mod.allocate_nodes(4, 2)
        initial_result = tort.tort_mod.uc_tort
        self.assertEqual(len(initial_result), 4)
        
        # Tear down
        tort.tort_mod.tear_down()
        
        # Should be empty after tear down
        cleared_result = tort.tort_mod.uc_tort
        self.assertEqual(len(cleared_result), 0)
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available") 
    def test_multiple_allocation_cycles(self):
        """Test multiple allocation/deallocation cycles work correctly."""
        # This tests memory management
        for i in range(3):
            tort.tort_mod.allocate_nodes(4 + i*2, 2 + i)
            result = tort.tort_mod.uc_tort
            expected_size = 2 * (2 + i)
            self.assertEqual(len(result), expected_size)
            tort.tort_mod.tear_down()
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_allocate_nodes_zero_values(self):
        """Test allocate_nodes with zero values."""
        # Should not crash - zero is valid input
        tort.tort_mod.allocate_nodes(0, 0)
        result = tort.tort_mod.uc_tort
        self.assertEqual(len(result), 0)
    
    # Replace the existing problematic tests with these 4 clear tests:
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_set_neighbours_raises_fortran_not_available_error_when_library_unavailable(self):
        """Test that set_neighbours raises FortranNotAvailableError when Fortran library not loaded."""
        from crystal_torture.exceptions import FortranNotAvailableError
        
        # Mock the Fortran library as not available
        with patch('crystal_torture.tort._tort_lib', None):
            with self.assertRaises(FortranNotAvailableError):
                tort.tort_mod.set_neighbours(0, 0, 1, [1])
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_set_neighbours_raises_runtime_error_when_not_allocated(self):
        """Test that set_neighbours raises RuntimeError when Fortran available but not allocated."""
        # Ensure clean state (not allocated, but Fortran library available)
        tort.tort_mod.tear_down()
        
        with self.assertRaises(RuntimeError) as context:
            tort.tort_mod.set_neighbours(0, 0, 1, [1])
        
        # Should have helpful guidance about proper setup
        message = str(context.exception)
        self.assertIn("graph_from_structure", message)
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")  
    def test_torture_raises_fortran_not_available_error_when_library_unavailable(self):
        """Test that torture raises FortranNotAvailableError when Fortran library not loaded."""
        from crystal_torture.exceptions import FortranNotAvailableError
        
        # Mock the Fortran library as not available
        with patch('crystal_torture.tort._tort_lib', None):
            with self.assertRaises(FortranNotAvailableError):
                tort.tort_mod.torture(1, [0])
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")  
    def test_torture_raises_runtime_error_when_not_allocated(self):
        """Test that torture raises RuntimeError when Fortran available but not allocated."""
        # Ensure clean state (not allocated, but Fortran library available)
        tort.tort_mod.tear_down()
        
        with self.assertRaises(RuntimeError) as context:
            tort.tort_mod.torture(1, [0])
        
        # Should have helpful guidance about proper setup
        message = str(context.exception)
        self.assertIn("graph_from_structure", message)
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_set_neighbours_empty_list(self):
        """Test set_neighbours with empty neighbour list."""
        tort.tort_mod.allocate_nodes(2, 1)
        # Should not crash - empty neighbour list is valid
        tort.tort_mod.set_neighbours(0, 0, 0, [])
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_set_neighbours_mismatched_count(self):
        """Test set_neighbours with mismatched count and list length."""
        tort.tort_mod.allocate_nodes(4, 2)
        # What happens when count doesn't match list length?
        # This might crash or behave unexpectedly
        try:
            tort.tort_mod.set_neighbours(0, 0, 2, [1])  # count=2, list has 1 element
        except (RuntimeError, IndexError, ValueError):
            pass  # Expected to fail
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_torture_empty_uc_nodes(self):
        """Test torture with empty uc_nodes list."""
        tort.tort_mod.allocate_nodes(2, 1)
        tort.tort_mod.set_neighbours(0, 0, 1, [1])
        # Should not crash - empty list is valid
        tort.tort_mod.torture(0, [])
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_tear_down_without_allocation(self):
        """Test tear_down without prior allocation."""
        # Should not crash - tear_down should be safe to call anytime
        tort.tort_mod.tear_down()
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_double_tear_down(self):
        """Test calling tear_down twice."""
        tort.tort_mod.allocate_nodes(2, 1)
        tort.tort_mod.tear_down()
        # Second tear_down should not crash
        tort.tort_mod.tear_down()
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_set_neighbours_works_after_allocation(self):
        """Test that set_neighbours works correctly when properly allocated."""
        tort.tort_mod.allocate_nodes(2, 1)
        # Should not raise any exception
        tort.tort_mod.set_neighbours(0, 0, 1, [1])
        
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_init_sets_not_allocated_state(self):
        """Test that __init__ initializes _is_allocated to False."""
        self.assertFalse(tort.tort_mod._is_allocated)
        
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")  
    def test_allocate_nodes_sets_allocated_state(self):
        """Test that allocate_nodes sets _is_allocated to True."""
        self.assertFalse(tort.tort_mod._is_allocated)  # Initially False
        tort.tort_mod.allocate_nodes(2, 1)
        self.assertTrue(tort.tort_mod._is_allocated)   # True after allocation
    
    @unittest.skipIf(tort.tort_mod is None, "Fortran not available")
    def test_tear_down_clears_allocated_state(self):
        """Test that tear_down sets _is_allocated to False."""
        tort.tort_mod.allocate_nodes(2, 1)
        self.assertTrue(tort.tort_mod._is_allocated)   # Should be True
        
        tort.tort_mod.tear_down()
        self.assertFalse(tort.tort_mod._is_allocated)  # Should be False after tear_down


class TestTortAvailability(unittest.TestCase):
    """Test how tort module handles Fortran availability."""
    
    def test_tort_import_doesnt_crash(self):
        """Test that importing tort module doesn't crash."""
        # This should work whether Fortran is available or not
        from crystal_torture import tort
        # tort.tort_mod might be None, but import should succeed
        
    def test_tort_mod_init_raises_fortran_not_available_error_when_unavailable(self):
        """Test that Tort_Mod.__init__ raises FortranNotAvailableError when Fortran unavailable."""
        with patch('crystal_torture.tort._FORT_AVAILABLE', False):
            from crystal_torture.tort import Tort_Mod
            
            with self.assertRaises(FortranNotAvailableError):
                Tort_Mod()


if __name__ == "__main__":
    unittest.main()