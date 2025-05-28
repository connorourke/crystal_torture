import unittest
from crystal_torture.minimal_cluster import minimal_Cluster


class MinimalClusterTestCase(unittest.TestCase):
	"""Test for minimal_Cluster class."""

	def setUp(self):
		self.site_indices = [0, 1, 2, 5]
		self.size = 4
		self.cluster = minimal_Cluster(self.site_indices, self.size)

	def test_minimal_cluster_initialisation(self):
		"""Test that minimal cluster initialises correctly."""
		self.assertEqual(self.cluster.site_indices, self.site_indices)
		self.assertEqual(self.cluster.size, self.size)
		self.assertIsNone(self.cluster.periodic)
		self.assertIsNone(self.cluster.tortuosity)

	def test_set_properties(self):
		"""Test that properties can be set."""
		self.cluster.periodic = 3
		self.cluster.tortuosity = 2.5
		
		self.assertEqual(self.cluster.periodic, 3)
		self.assertEqual(self.cluster.tortuosity, 2.5)


if __name__ == "__main__":
	unittest.main()