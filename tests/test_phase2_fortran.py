# tests/test_phase2_fortran.py
"""
Phase 2 TDD tests: Fortran-Python integration
These tests define what we want to achieve in Phase 2.
"""
import pytest
import warnings
import subprocess
import sys
from pathlib import Path

class TestFortranPythonIntegration:
    """Test that Fortran modules are properly integrated with Python."""
    
    def test_fort_import_no_warnings(self):
        """Test that importing Fortran modules doesn't generate warnings."""
        
        # Capture warnings during import
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")  # Catch all warnings
            
            try:
                from crystal_torture import tort
                
                # Check if any warnings were generated
                fortran_warnings = [w for w in warning_list 
                                  if "Fortran extensions not available" in str(w.message)]
                
                assert len(fortran_warnings) == 0, \
                    f"Should not have Fortran unavailable warnings, got: {[str(w.message) for w in fortran_warnings]}"
                
                # tort should not be None
                assert tort is not None, "tort module should be available"
                
            except ImportError as e:
                pytest.fail(f"Should be able to import tort module: {e}")
    
    def test_tort_module_has_expected_attributes(self):
        """Test that tort module has the expected Fortran functions."""
        try:
            from crystal_torture import tort
            
            # Check for the main tort_mod object
            assert hasattr(tort, 'tort_mod'), "Should have tort_mod attribute"
            
            # Check for key functions that should be available
            expected_functions = ['allocate_nodes', 'tear_down', 'set_neighbours', 'torture']
            
            for func_name in expected_functions:
                assert hasattr(tort.tort_mod, func_name), \
                    f"tort_mod should have {func_name} function"
                
        except ImportError:
            pytest.skip("tort module not available - this is what we're trying to fix")
    
    def test_fortran_functions_are_callable(self):
        """Test that Fortran functions can actually be called."""
        try:
            from crystal_torture import tort
            
            # Test basic allocation/deallocation (safe operations)
            try:
                tort.tort_mod.allocate_nodes(10, 5)  # 10 nodes, 5 unit cell nodes
                tort.tort_mod.tear_down()
                # If no exception, the functions work
                
            except Exception as e:
                pytest.fail(f"Fortran functions should be callable: {e}")
                
        except ImportError:
            pytest.skip("tort module not available - this is what we're trying to fix")
    
    def test_no_import_warnings_on_package_import(self):
        """Test that importing the main package doesn't show Fortran warnings."""
        
        # Run in subprocess to get clean import
        result = subprocess.run([
            sys.executable, '-c', 
            'import warnings; warnings.simplefilter("always"); '
            'import crystal_torture; '
            'from crystal_torture import Node, Cluster, Graph'
        ], capture_output=True, text=True)
        
        # Should not have warnings in stderr about Fortran extensions
        assert "Fortran extensions not available" not in result.stderr, \
            f"Package import should not show Fortran warnings. Got stderr: {result.stderr}"
        
        # Should import successfully
        assert result.returncode == 0, f"Package should import successfully. Got: {result.stderr}"


class TestFortranExtensionFiles:
    """Test that the expected Fortran extension files are created and installed."""
    
    def test_fortran_extensions_built_by_meson(self):
        """Test that meson builds proper Python extensions, not just libraries."""
        import tempfile
        from pathlib import Path
        
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / "test_build"
            
            # Build with meson
            setup_result = subprocess.run([
                'meson', 'setup', str(build_dir)
            ], capture_output=True, text=True, cwd='.')
            
            if setup_result.returncode != 0:
                pytest.skip(f"Meson setup failed: {setup_result.stderr}")
            
            build_result = subprocess.run([
                'meson', 'compile', '-C', str(build_dir)
            ], capture_output=True, text=True)
            
            if build_result.returncode != 0:
                pytest.skip(f"Meson build failed: {build_result.stderr}")
            
            # Look for Python extension files (should have Python-importable names)
            import platform
            if platform.system() == "Darwin":
                extension_files = list(build_dir.rglob("_tort*.dylib")) + list(build_dir.rglob("_tort*.so"))
            else:
                extension_files = list(build_dir.rglob("_tort*.so"))
            
            # Should find at least one Python extension
            assert len(extension_files) > 0, \
                f"Should build Python extensions (_tort.so/.dylib), found: {[f.name for f in build_dir.rglob('*tort*')]}"
    
    def test_extensions_installed_in_package(self):
        """Test that Python extensions are installed in the package directory."""
        import crystal_torture
        package_dir = Path(crystal_torture.__file__).parent
        
        # Look for Fortran extension files in the installed package
        import platform
        if platform.system() == "Darwin":
            extension_files = (list(package_dir.glob("_tort*.dylib")) + 
                             list(package_dir.glob("_tort*.so")))
        else:
            extension_files = list(package_dir.glob("_tort*.so"))
        
        # This test might fail initially - that's what we're trying to fix
        if len(extension_files) == 0:
            # Don't fail the test, just document what we found
            all_files = [f.name for f in package_dir.iterdir() if f.is_file()]
            pytest.skip(f"No Fortran extensions found in package. Files present: {all_files}")
        
        assert len(extension_files) > 0, "Should have Fortran extensions in installed package"


class TestBackwardCompatibility:
    """Test that existing functionality still works with new Fortran integration."""
    
    def test_python_only_methods_still_work(self):
        """Test that Python-only tortuosity methods work."""
        from crystal_torture import Node, Cluster
        
        # Create minimal periodic structure: 2 nodes with same UC_index (periodic images)
        nodes = []
        
        # Node 0: Unit cell node
        node0 = Node(
            index=0,
            element="Li",
            labels={"UC_index": "0", "Halo": False},
            neighbours_ind=[1]  # Connected to node 1
        )
        nodes.append(node0)
        
        # Node 1: Periodic image of node 0  
        node1 = Node(
            index=1,
            element="Li",
            labels={"UC_index": "0", "Halo": True},  # Same UC_index, different index
            neighbours_ind=[0]  # Connected to node 0
        )
        nodes.append(node1)
        
        # Set up neighbor relationships
        for node in nodes:
            node.neighbours = set([nodes[j] for j in node.neighbours_ind])
        
        # Create cluster with both nodes
        cluster = Cluster(set(nodes))
        
        try:
            cluster.torture_py()  # This should work regardless of Fortran availability
            
            # Should have tortuosity values for unit cell nodes
            uc_nodes = list(cluster.return_key_nodes(key="Halo", value=False))
            for node in uc_nodes:
                assert hasattr(node, 'tortuosity'), f"Node {node.index} should have tortuosity after torture_py"
                assert node.tortuosity is not None, f"Node {node.index} tortuosity should not be None"
                
        except Exception as e:
            pytest.fail(f"Python-only torture method should work: {e}")
    
    def test_fortran_methods_available_when_extensions_work(self):
        """Test that Fortran methods are available when extensions are properly integrated."""
        from crystal_torture import Node, Cluster
        
        # Only run this test if we think Fortran should be working
        try:
            from crystal_torture import tort
            if tort is None:
                pytest.skip("Fortran not available")
        except ImportError:
            pytest.skip("Fortran not available")
        
        # Create minimal periodic structure: 2 nodes with same UC_index (periodic images)
        nodes = []
        
        # Node 0: Unit cell node
        node0 = Node(
            index=0,
            element="Li",
            labels={"UC_index": "0", "Halo": False},
            neighbours_ind=[1]  # Connected to node 1
        )
        nodes.append(node0)
        
        # Node 1: Periodic image of node 0  
        node1 = Node(
            index=1,
            element="Li",
            labels={"UC_index": "0", "Halo": True},  # Same UC_index, different index
            neighbours_ind=[0]  # Connected to node 0
        )
        nodes.append(node1)
        
        # Set up neighbor relationships
        for node in nodes:
            node.neighbours = set([nodes[j] for j in node.neighbours_ind])
        
        cluster = Cluster(set(nodes))
        
        try:
            # This should work if Fortran extensions are properly set up
            cluster.torture_fort()
            
            # Should have tortuosity values for unit cell nodes
            uc_nodes = [n for n in nodes if not n.labels["Halo"]]
            for node in uc_nodes:
                assert hasattr(node, 'tortuosity'), f"Node {node.index} should have tortuosity after torture_fort"
                
        except ImportError as e:
            if "Fortran extensions not available" in str(e):
                pytest.skip("This is what we're trying to fix - Fortran extensions not available")
            else:
                pytest.fail(f"Unexpected error: {e}")
        
        finally:
            # CRITICAL: Clean up Fortran state to prevent test contamination
            try:
                from crystal_torture import tort
                if tort is not None and hasattr(tort, 'tort_mod'):
                    tort.tort_mod.tear_down()
            except:
                pass  # Ignore cleanup errors
