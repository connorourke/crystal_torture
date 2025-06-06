import unittest
from crystal_torture.node import Node
import warnings


class NodeTestCase(unittest.TestCase):
    """Test for Site Class"""

    def setUp(self):
        self.index = 1
        self.element = "Mg"
        self.uc_index = 2
        self.is_halo = False
        self.neighbours_ind = [1, 2, 9, 10]
        self.node = Node(
            self.index,
            self.element,
            self.uc_index,
            self.is_halo,
            self.neighbours_ind
        )

    def test_node_is_initialised(self):
        self.assertEqual(self.node.index, self.index)
        self.assertEqual(self.node.element, self.element)
        self.assertEqual(self.node.uc_index, self.uc_index)
        self.assertEqual(self.node.is_halo, self.is_halo)
        self.assertEqual(self.node.neighbours_ind, self.neighbours_ind)
    
    def test_node_labels_backward_compatibility(self):
        """Test that deprecated labels interface still works."""
        node = Node(
            index=5,
            element="Li", 
            uc_index=2,
            is_halo=True,
            neighbours_ind={1, 3}
        )
        
        # Suppress deprecation warning for this test since we're specifically testing functionality
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            labels = node.labels
        
        self.assertEqual(labels["UC_index"], "2")
        self.assertEqual(labels["Halo"], True)
            
    def test_node_with_default_parameters(self):
        """Test that optional parameters default correctly."""
        node = Node(0, "Li", uc_index=1, is_halo=True)
        
        self.assertEqual(node.neighbours_ind, set())
        self.assertIsNone(node.neighbours)
        self.assertIsNone(node.tortuosity)
        self.assertEqual(node.dist, 0)
        
    def test_node_tortuosity_and_dist_modification(self):
        """Test that tortuosity and dist can be modified after creation."""
        node = Node(0, "Li", uc_index=1, is_halo=False, neighbours_ind=set())
        
        # Test initial values
        self.assertIsNone(node.tortuosity)
        self.assertEqual(node.dist, 0)
        
        # Test modification
        node.tortuosity = 3.5
        node.dist = 5
        
        self.assertEqual(node.tortuosity, 3.5)
        self.assertEqual(node.dist, 5)
        
    def test_node_with_empty_neighbours(self):
        """Test node creation with explicitly empty neighbours."""
        node = Node(0, "O", uc_index=0, is_halo=True, neighbours_ind=set(), neighbours=set())
        
        self.assertEqual(node.neighbours_ind, set())
        self.assertEqual(node.neighbours, set())
        
    def test_node_labels_deprecation_warning(self):
        """Test that accessing labels property raises deprecation warning."""
        node = Node(0, "Li", uc_index=1, is_halo=False, neighbours_ind=set())
        
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            
            # Access the deprecated property
            labels = node.labels
            
            # Should have raised exactly one deprecation warning
            self.assertEqual(len(warning_list), 1)
            warning = warning_list[0]
            
            # Check warning properties
            self.assertTrue(issubclass(warning.category, DeprecationWarning))
            self.assertIn("labels is deprecated", str(warning.message))
            self.assertIn("node.uc_index and node.is_halo", str(warning.message))
            
            # Property should still work for backward compatibility
            self.assertEqual(labels["UC_index"], "1")
            self.assertEqual(labels["Halo"], False)


if __name__ == "__main__":
    unittest.main()
