import unittest
from crystal_torture import Node
import warnings


class NodeTestCase(unittest.TestCase):
    """Test for Site Class"""

    def setUp(self):
        self.index = 1
        self.element = "Mg"
        self.labels = {1: "A", 2: str(self.index)}
        self.neighbours_ind = [1, 2, 9, 10]
        self.node = Node(
            self.index,
            self.element,
            self.labels,
            self.neighbours_ind
        )

    def test_node_is_initialised(self):
        self.assertEqual(self.node.index, self.index)
        self.assertEqual(self.node.element, self.element)
        self.assertEqual(self.node.labels, self.labels)
        self.assertEqual(self.node.neighbours_ind, self.neighbours_ind)
        
    def test_node_new_attributes_basic(self):
        """Test that new uc_index and is_halo attributes work correctly."""
        node = Node(
            index=5,
            element="Li",
            uc_index=2,
            is_halo=True,
            neighbours_ind={1, 3}
        )
        
        self.assertEqual(node.uc_index, 2)
        self.assertEqual(node.is_halo, True)
        self.assertIsInstance(node.uc_index, int)
        self.assertIsInstance(node.is_halo, bool)
    
    def test_node_labels_backward_compatibility(self):
        """Test that deprecated labels interface still works."""
        node = Node(
            index=5,
            element="Li", 
            uc_index=2,
            is_halo=True,
            neighbours_ind={1, 3}
        )
        
        # Access labels should work (no warnings for now)
        labels = node.labels
        
        self.assertEqual(labels["UC_index"], "2")  # String for compatibility
        self.assertEqual(labels["Halo"], True)     # Boolean unchanged
    
    def test_node_labels_from_old_api(self):
        """Test that old labels API still works."""
        node = Node(
            index=0, 
            element="Li", 
            labels={"UC_index": "1", "Halo": False, "other": "value"},
            neighbours_ind=set()
        )
        
        # Should extract values from labels
        self.assertEqual(node.uc_index, 1)  # Converted to int
        self.assertEqual(node.is_halo, False)
        
        # Labels should preserve original values plus extracted ones
        labels = node.labels
        self.assertEqual(labels["UC_index"], "1")
        self.assertEqual(labels["Halo"], False)
        self.assertEqual(labels["other"], "value")  # Original preserved
    
    def test_node_new_vs_old_api_consistency(self):
        """Test that new and old APIs give consistent values."""
        test_cases = [
            (0, False),
            (5, True), 
            (999, False)
        ]
        
        for uc_index, is_halo in test_cases:
            node = Node(
                index=10,
                element="Mg",
                uc_index=uc_index,
                is_halo=is_halo,
                neighbours_ind={1, 2}
            )
            
            # New API
            self.assertEqual(node.uc_index, uc_index)
            self.assertEqual(node.is_halo, is_halo)
            
            # Old API
            self.assertEqual(int(node.labels["UC_index"]), uc_index)
            self.assertEqual(node.labels["Halo"], is_halo)
    
    def test_node_optional_attributes(self):
        """Test that uc_index and is_halo are optional."""
        # Node with neither new params nor proper labels
        node = Node(
            index=1,
            element="O",
            labels={"arbitrary": "value"},
            neighbours_ind=set()
        )
        
        self.assertIsNone(node.uc_index)
        self.assertIsNone(node.is_halo)
        
        # Labels should preserve original
        labels = node.labels
        self.assertEqual(labels["arbitrary"], "value")
        self.assertNotIn("UC_index", labels)  # Since uc_index is None
        self.assertNotIn("Halo", labels)      # Since is_halo is None


if __name__ == "__main__":
    unittest.main()
