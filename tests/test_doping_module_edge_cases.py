import unittest
from pymatgen.core import Structure, Lattice
from crystal_torture.pymatgen_doping import (
	count_sites, index_sites, dope_structure, dope_structure_by_no
)


class DopingEdgeCasesTestCase(unittest.TestCase):
	"""Test edge cases for doping module functions."""

	def setUp(self):
		"""Set up simple structure for testing."""
		lattice = Lattice.cubic(4.0)
		self.structure = Structure(
			lattice, 
			["Li", "Li", "Mg", "Mg"], 
			[[0, 0, 0], [0.5, 0, 0], [0, 0.5, 0], [0.5, 0.5, 0]]
		)
		# Set some labels
		for i, site in enumerate(self.structure.sites):
			site.label = "A" if i < 2 else "B"

	def test_count_sites_no_matches(self):
		"""Test count_sites when no sites match criteria."""
		count = count_sites(self.structure, species={"Na"})
		self.assertEqual(count, 0)
		
		count = count_sites(self.structure, labels={"C"})
		self.assertEqual(count, 0)

	def test_index_sites_no_matches(self):
		"""Test index_sites when no sites match criteria."""
		indices = index_sites(self.structure, species={"Na"})
		self.assertEqual(indices, [])
		
		indices = index_sites(self.structure, labels={"C"})
		self.assertEqual(indices, [])

	def test_count_sites_both_species_and_labels(self):
		"""Test count_sites with both species and labels specified."""
		count = count_sites(self.structure, species={"Li"}, labels={"A"})
		self.assertEqual(count, 2)  # Both Li sites have label A
		
		count = count_sites(self.structure, species={"Li"}, labels={"B"})
		self.assertEqual(count, 0)  # No Li sites have label B

	def test_index_sites_both_species_and_labels(self):
		"""Test index_sites with both species and labels specified."""
		indices = index_sites(self.structure, species={"Mg"}, labels={"B"})
		self.assertEqual(set(indices), {2, 3})  # Both Mg sites have label B

	def test_dope_structure_zero_concentration(self):
		"""Test doping with zero concentration."""
		original_structure = self.structure.copy()
		doped = dope_structure(original_structure, 0.0, "Li", ["Na"])
		
		# Should have no Na atoms
		na_count = count_sites(doped, species={"Na"})
		self.assertEqual(na_count, 0)

	def test_dope_structure_by_no_zero_dopants(self):
		"""Test doping by number with zero dopants."""
		original_structure = self.structure.copy()
		doped = dope_structure_by_no(original_structure, 0, "Li", ["Na"])
		
		# Should have no Na atoms
		na_count = count_sites(doped, species={"Na"})
		self.assertEqual(na_count, 0)

	def test_dope_structure_multiple_dopants(self):
		"""Test doping with multiple dopant species."""
		original_structure = self.structure.copy()
		doped = dope_structure_by_no(original_structure, 1, "Li", ["Na", "K"], label_to_remove="A")
		
		# Should have 1 Na and 1 K
		na_count = count_sites(doped, species={"Na"})
		k_count = count_sites(doped, species={"K"})
		self.assertEqual(na_count, 1)
		self.assertEqual(k_count, 1)
		
		# Should have 0 Li atoms remaining
		li_count = count_sites(doped, species={"Li"})
		self.assertEqual(li_count, 0)


if __name__ == "__main__":
	unittest.main()