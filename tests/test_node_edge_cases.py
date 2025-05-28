import unittest
from crystal_torture import Node


class NodeEdgeCasesTestCase(unittest.TestCase):
	"""Test edge cases for Node class."""

	def test_node_with_empty_neighbours(self):
		"""Test node with empty neighbour set."""
		node = Node(
			index=0,
			element="Li", 
			labels={"test": "value"},
			neighbours_ind=set(),
			neighbours=set()
		)
		
		self.assertEqual(node.index, 0)
		self.assertEqual(node.element, "Li")
		self.assertEqual(node.neighbours_ind, set())
		self.assertEqual(node.neighbours, set())

	def test_node_default_values(self):
		"""Test node default values are set correctly."""
		node = Node(
			index=1,
			element="Mg",
			labels={},
			neighbours_ind={2, 3}
		)
		
		self.assertIsNone(node.neighbours)
		self.assertIsNone(node.tortuosity)
		self.assertEqual(node.dist, 0)

	def test_node_with_complex_labels(self):
		"""Test node with complex label dictionary."""
		complex_labels = {
			"UC_index": "5",
			"Halo": True,
			1: "numeric_key",
			"list_value": [1, 2, 3]
		}
		
		node = Node(
			index=10,
			element="O",
			labels=complex_labels,
			neighbours_ind={1, 2, 3, 4, 5}
		)
		
		self.assertEqual(node.labels, complex_labels)
		self.assertEqual(len(node.neighbours_ind), 5)

	def test_node_tortuosity_can_be_set(self):
		"""Test that node tortuosity can be set after creation."""
		node = Node(0, "Li", {}, set())
		
		self.assertIsNone(node.tortuosity)
		
		node.tortuosity = 3.5
		self.assertEqual(node.tortuosity, 3.5)

	def test_node_dist_can_be_modified(self):
		"""Test that node dist property can be modified."""
		node = Node(0, "Li", {}, set())
		
		self.assertEqual(node.dist, 0)
		
		node.dist = 5
		self.assertEqual(node.dist, 5)


if __name__ == "__main__":
	unittest.main()