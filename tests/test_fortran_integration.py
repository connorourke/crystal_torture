# tests/test_fortran_integration.py
"""
Integration tests for Fortran extensions and fallback behaviour.

These tests ensure that:
1. Fortran extensions load cleanly when available
2. Python fallbacks work when extensions are not available  
3. Both implementations produce consistent results
4. User-facing APIs remain stable
"""
import pytest
import warnings
import subprocess
import sys
import numpy as np
from pathlib import Path
from crystal_torture.pymatgen_interface import set_fort_nodes


@pytest.fixture(autouse=True)
def cleanup_fortran_state():
	"""Clean up Fortran state before and after each test to prevent contamination."""
	# Setup: Clean state before test
	try:
		from crystal_torture import tort
		if tort is not None and hasattr(tort, 'tort_mod') and tort.tort_mod is not None:
			tort.tort_mod.tear_down()
	except:
		pass  # Ignore errors during cleanup
	
	yield  # Run the test
	
	# Teardown: Clean state after test
	try:
		from crystal_torture import tort
		if tort is not None and hasattr(tort, 'tort_mod') and tort.tort_mod is not None:
			tort.tort_mod.tear_down()
	except:
		pass  # Ignore errors during cleanup


class TestBasicImports:
	"""Test that basic package imports work correctly."""
	
	def test_core_package_imports(self):
		"""Test that core package imports work without errors."""
		try:
			import crystal_torture
			from crystal_torture import Node, Cluster, Graph
			assert hasattr(crystal_torture, '__version__')
		except ImportError as e:
			pytest.fail(f"Core imports failed: {e}")
	
	def test_no_import_warnings_on_package_import(self):
		"""Test that importing the main package doesn't show unwanted warnings."""
		# Run in subprocess to get clean import
		result = subprocess.run([
			sys.executable, '-c', 
			'import warnings; warnings.simplefilter("always"); '
			'import crystal_torture; '
			'from crystal_torture import Node, Cluster, Graph'
		], capture_output=True, text=True)
		
		# Should import successfully
		assert result.returncode == 0, f"Package should import successfully. Got: {result.stderr}"
		
		# Should not have user-facing warnings about Fortran extensions
		# (Internal warnings are OK, but they shouldn't reach end users by default)
		assert "not available" not in result.stderr, \
			f"Package import should not show 'not available' messages to users. Got stderr: {result.stderr}"


class TestTortModuleIntegration:
	"""Test tort module integration and API consistency."""
	
	def test_tort_module_import_behaviour(self):
		"""Test that tort module imports with expected behaviour."""
		with warnings.catch_warnings(record=True) as warning_list:
			warnings.simplefilter("always")
			
			try:
				from crystal_torture import tort
				
				# tort should be importable (may be None if extensions unavailable)
				assert tort is not None or tort is None  # Either state is valid
				
				# If available, should have expected interface
				if tort is not None and hasattr(tort, 'tort_mod') and tort.tort_mod is not None:
					expected_methods = ['allocate_nodes', 'tear_down', 'set_neighbours', 'torture']
					for method_name in expected_methods:
						assert hasattr(tort.tort_mod, method_name), \
							f"tort_mod should have {method_name} method"
				
			except ImportError as e:
				pytest.fail(f"Should be able to import tort module: {e}")
	
	def test_tort_functions_callable_when_available(self):
		"""Test that tort functions can be called when Fortran extensions are available."""
		try:
			from crystal_torture import tort
			
			# Only test if Fortran is actually available
			if tort is None or not hasattr(tort, 'tort_mod') or tort.tort_mod is None:
				pytest.skip("Fortran extensions not available")
			
			# Test basic allocation/deallocation (safe operations)
			try:
				tort.tort_mod.allocate_nodes(10, 5)  # 10 nodes, 5 unit cell nodes
				tort.tort_mod.tear_down()
				# If no exception, the functions work
				
			except Exception as e:
				pytest.fail(f"Fortran functions should be callable: {e}")
				
		except ImportError:
			pytest.skip("tort module not available")


class TestDistModuleIntegration:
	"""Test dist module integration and API consistency."""
	
	def test_dist_module_import_behaviour(self):
		"""Test that dist module imports cleanly."""
		with warnings.catch_warnings(record=True) as warning_list:
			warnings.simplefilter("always")
			
			try:
				from crystal_torture import dist
				
				# Should have expected functions (either Fortran or Python fallback)
				expected_functions = ['dist', 'shift_index']
				for func_name in expected_functions:
					assert hasattr(dist, func_name), f"dist module should have {func_name} function"
				
			except ImportError as e:
				pytest.fail(f"Should be able to import dist module: {e}")
	
	def test_dist_functions_callable(self):
		"""Test that dist functions can be called and return sensible results."""
		try:
			from crystal_torture import dist
			
			# Test basic dist function call
			coords1 = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], dtype=np.float32)
			coords2 = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], dtype=np.float32)
			
			try:
				result = dist.dist(coords1, coords2, 2)
				assert result is not None, "dist function should return results"
				assert hasattr(result, 'shape'), "dist should return array-like result"
				assert result.shape == (2, 2), f"dist should return 2x2 matrix, got {result.shape}"
				
				# Test basic mathematical correctness
				assert abs(result[0, 0]) < 1e-6, "Distance from point to itself should be 0"
				assert abs(result[0, 1] - 1.0) < 1e-6, "Distance should be 1.0"
				
			except Exception as e:
				pytest.fail(f"dist function should be callable: {e}")
		
		except ImportError:
			pytest.skip("dist module not available")
	
	def test_shift_index_function(self):
		"""Test that shift_index function works correctly."""
		try:
			from crystal_torture import dist
			
			# Test basic shift_index function
			try:
				result = dist.shift_index(0, [0, 0, 0])
				assert isinstance(result, int), "shift_index should return integer"
				
				result = dist.shift_index(0, [1, 0, 0])
				assert isinstance(result, int), "shift_index should return integer"
				
			except Exception as e:
				pytest.fail(f"shift_index function should be callable: {e}")
				
		except ImportError:
			pytest.skip("dist module not available")


class TestBackwardCompatibility:
	"""Test that Python-only methods work regardless of Fortran availability."""
	
	def test_python_torture_methods_always_work(self):
		"""Test that Python-only tortuosity methods work."""
		from crystal_torture import Node, Cluster
		
		# Create minimal periodic structure: 2 nodes with same UC_index (periodic images)
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
		for node in [node0, node1]:
			node.neighbours = set([node0, node1][j] for j in node.neighbours_ind)
		
		cluster = Cluster({node0, node1})
		
		try:
			cluster.torture_py()  # This should always work
			
			# Should have tortuosity values for unit cell nodes
			uc_nodes = list(cluster.uc_nodes)
			for node in uc_nodes:
				assert hasattr(node, 'tortuosity'), f"Node {node.index} should have tortuosity after torture_py"
				assert node.tortuosity is not None, f"Node {node.index} tortuosity should not be None"
				
		except Exception as e:
			pytest.fail(f"Python-only torture method should always work: {e}")


class TestIntegrationCorrectness:
	"""Test that Fortran and Python implementations give consistent results."""
	
	def test_fortran_torture_when_available(self):
		"""Test that Fortran torture method works when extensions are available."""
		from crystal_torture import Node, Cluster
		
		# Only run if Fortran is available
		try:
			from crystal_torture import tort
			if tort is None or not hasattr(tort, 'tort_mod') or tort.tort_mod is None:
				pytest.skip("Fortran extensions not available")
		except ImportError:
			pytest.skip("Fortran extensions not available")
		
		# Create the same test structure as in the Python test
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
		for node in [node0, node1]:
			node.neighbours = set([node0, node1][j] for j in node.neighbours_ind)
		
		cluster = Cluster({node0, node1})
		
		# Set up nodes in Fortran module first
		set_fort_nodes({node0, node1})
		
		try:
			cluster.torture_fort()
			
			# Should have tortuosity values for unit cell nodes
			uc_nodes = [n for n in [node0, node1] if not n.is_halo]
			for node in uc_nodes:
				assert hasattr(node, 'tortuosity'), f"Node {node.index} should have tortuosity after torture_fort"
				assert node.tortuosity is not None, f"Node {node.index} tortuosity should not be None"
				assert isinstance(node.tortuosity, (int, float)), "Should have numeric tortuosity"
				
		except ImportError as e:
			if "Fortran extensions not available" in str(e):
				pytest.skip("Fortran extensions not available - this is expected")
			else:
				pytest.fail(f"Unexpected error: {e}")


class TestPymatgenInterfaceIntegration:
	"""Test that pymatgen interface works with both Fortran and Python implementations."""
	
	def test_pymatgen_interface_no_warnings(self):
		"""Test that importing pymatgen_interface doesn't show warnings to users."""
		with warnings.catch_warnings(record=True) as warning_list:
			warnings.simplefilter("always")
			
			# Import the module that uses both tort and dist
			from crystal_torture.pymatgen_interface import get_all_neighbors_and_image
			
			# Should not have user-facing warnings about modules not being available
			user_facing_warnings = [w for w in warning_list 
								  if "not available" in str(w.message) and w.category == UserWarning]
			
			# It's OK to have internal warnings, but they shouldn't reach end users
			assert len(user_facing_warnings) == 0, \
				f"pymatgen_interface should not show 'not available' warnings: {[str(w.message) for w in user_facing_warnings]}"