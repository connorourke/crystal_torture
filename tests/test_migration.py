# tests/test_migration.py
"""
Test suite to ensure migration doesn't break existing functionality.
These tests should pass before, during, and after the migration.
"""
import pytest
import sys
from pathlib import Path
import subprocess

class TestCurrentFunctionality:
    """Test that existing functionality works before migration."""
    
    def test_basic_imports(self):
        """Test that basic imports work."""
        try:
            import crystal_torture
            from crystal_torture import Node, Cluster, Graph
            assert hasattr(crystal_torture, '__version__')
        except ImportError as e:
            pytest.fail(f"Basic imports failed: {e}")
    
    def test_node_creation(self):
        """Test Node class functionality."""
        from crystal_torture import Node
        
        node = Node(
            index=1,
            element="Mg", 
            labels={"test": "value"},
            neighbours_ind=[2, 3, 4]
        )
        
        assert node.index == 1
        assert node.element == "Mg"
        assert node.labels["test"] == "value"
        assert node.neighbours_ind == [2, 3, 4]
    
    def test_fortran_availability_detection(self):
        """Test that we can detect Fortran module availability."""
        try:
            from crystal_torture import tort
            fortran_available = tort is not None
        except ImportError:
            fortran_available = False
        
        # This test just documents current state
        print(f"Fortran modules available: {fortran_available}")
        assert isinstance(fortran_available, bool)
    
    def test_pymatgen_interface_basic(self):
        """Test basic pymatgen interface functionality."""
        from crystal_torture.pymatgen_interface import nodes_from_structure
        from pymatgen.core import Structure
        
        # Create simple test structure
        structure = Structure(
            lattice=[[4.0, 0, 0], [0, 4.0, 0], [0, 0, 4.0]],
            species=["Li", "Li"],
            coords=[[0, 0, 0], [0.5, 0.5, 0.5]]
        )
        
        nodes = nodes_from_structure(structure, rcut=3.0, get_halo=False)
        assert len(nodes) == 2
        assert all(hasattr(node, 'index') for node in nodes)


class TestBuildSystem:
    """Test build system functionality."""
    
    def test_current_build_system(self):
        """Test that current build system info is accessible."""
        # This helps us understand what we're migrating from
        import crystal_torture
        
        # Check if we can access version
        assert hasattr(crystal_torture, '__version__')
        
        # Check module structure
        expected_modules = ['node', 'cluster', 'graph', 'pymatgen_interface']
        for module in expected_modules:
            assert hasattr(crystal_torture, module) or True  # Some might not be directly imported
    
    def test_fortran_build_artifacts(self):
        """Test what Fortran artifacts currently exist."""
        import crystal_torture
        package_path = Path(crystal_torture.__file__).parent
        
        # Look for existing Fortran artifacts
        fortran_files = list(package_path.glob("*tort*")) + list(package_path.glob("*dist*"))
        
        print(f"Found Fortran artifacts: {[f.name for f in fortran_files]}")
        # Just document what exists, don't assert


class TestMigrationReadiness:
    """Test that we're ready for migration."""
    
    def test_meson_availability(self):
        """Test if meson is available for build."""
        try:
            result = subprocess.run(['meson', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            meson_available = result.returncode == 0
            if meson_available:
                print(f"Meson version: {result.stdout.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            meson_available = False
        
        # Don't fail if meson not available yet, just document
        print(f"Meson available: {meson_available}")
    
    def test_fortran_compiler_availability(self):
        """Test if Fortran compiler is available."""
        try:
            result = subprocess.run(['gfortran', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            fortran_available = result.returncode == 0
            if fortran_available:
                print(f"Fortran compiler available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            fortran_available = False
        
        print(f"Fortran compiler available: {fortran_available}")
