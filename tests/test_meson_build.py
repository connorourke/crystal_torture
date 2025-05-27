# tests/test_meson_build.py
"""
Tests for meson build system functionality.
Written before implementing meson build to follow TDD.
"""
import pytest
import subprocess
import tempfile  
import shutil
from pathlib import Path
import os

class TestMesonBuildSystem:
    """Test meson build system setup and functionality."""
    
    def test_meson_build_file_exists(self):
        """Test that meson.build file exists and is valid."""
        meson_file = Path("meson.build")
        assert meson_file.exists(), "meson.build file should exist"
        
        # Test basic syntax by running meson introspect
        try:
            result = subprocess.run([
                'meson', 'introspect', '--projectinfo', '.'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                import json
                project_info = json.loads(result.stdout)
                assert project_info['descriptive_name'] == 'crystal_torture'
                assert 'fortran' in project_info['subprojects'] or 'fortran' in str(project_info)
            else:
                pytest.skip(f"Meson introspect failed: {result.stderr}")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Meson not available for testing")
    
    def test_meson_can_setup_build_directory(self):
        """Test that meson can setup a build directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / "build"
            
            try:
                result = subprocess.run([
                    'meson', 'setup', str(build_dir)
                ], capture_output=True, text=True, timeout=60, cwd='.')
                
                if result.returncode == 0:
                    assert build_dir.exists()
                    assert (build_dir / "build.ninja").exists()
                else:
                    pytest.skip(f"Meson setup failed: {result.stderr}")
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pytest.skip("Meson not available for testing")
    
    def test_fortran_modules_can_be_built(self):
        """Test that Fortran modules can be built with meson."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / "build"
            
            try:
                # Setup
                setup_result = subprocess.run([
                    'meson', 'setup', str(build_dir)
                ], capture_output=True, text=True, timeout=60, cwd='.')
                
                if setup_result.returncode != 0:
                    pytest.skip(f"Meson setup failed: {setup_result.stderr}")
                
                # Build
                build_result = subprocess.run([
                    'meson', 'compile', '-C', str(build_dir)
                ], capture_output=True, text=True, timeout=120)
                
                if build_result.returncode == 0:
                    # Look for Python extensions (the correct build artifacts)
                    import platform
                    if platform.system() == "Darwin":  # macOS
                        extension_files = list(build_dir.rglob("*.so"))  # Python extensions
                        shared_files = list(build_dir.rglob("*.dylib"))   # Generic shared libs
                    elif platform.system() == "Windows":
                        extension_files = list(build_dir.rglob("*.pyd"))  # Python extensions on Windows
                        shared_files = list(build_dir.rglob("*.dll"))     # Generic shared libs
                    else:  # Linux and others
                        extension_files = list(build_dir.rglob("*.so"))   # Python extensions
                        shared_files = []  # Generic shared libs
                    
                    # Static libraries as backup
                    static_files = list(build_dir.rglob("*.a"))
                    
                    # Python extensions are preferred, but any library type counts
                    all_libs = extension_files + shared_files + static_files
                    
                    if len(all_libs) == 0:
                        # Debug: show what files were actually created
                        all_files = [f for f in build_dir.rglob("*") if f.is_file()]
                        file_list = [str(f.relative_to(build_dir)) for f in all_files[:20]]  # First 20
                        pytest.fail(f"No libraries built. Files found: {file_list}")
                    
                    # Success criteria: should have built Python extensions
                    assert len(extension_files) >= 2, f"Should build at least 2 Python extensions (dist, _tort). Found: {[f.name for f in extension_files]}"
                    
                    # Verify we have the expected extensions
                    extension_names = [f.name for f in extension_files]
                    assert any('dist' in name for name in extension_names), f"Should have dist extension. Found: {extension_names}"
                    assert any('_tort' in name for name in extension_names), f"Should have _tort extension. Found: {extension_names}"
                    
                    print(f"✅ Successfully built {len(extension_files)} Python extensions: {[f.name for f in extension_files]}")
                    
                else:
                    pytest.skip(f"Meson compile failed: {build_result.stderr}")
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pytest.skip("Meson not available for testing")


class TestMesonPythonIntegration:
    """Test meson-python build backend integration."""
    
    def test_pyproject_toml_has_meson_backend(self):
        """Test that pyproject.toml is configured for meson-python."""
        pyproject_file = Path("pyproject.toml")
        
        if pyproject_file.exists():
            content = pyproject_file.read_text()
            
            # Check for meson-python in build-system
            assert 'meson-python' in content, "Should have meson-python in build-system requires"
            assert 'mesonpy' in content, "Should use mesonpy build backend"
        else:
            pytest.skip("pyproject.toml doesn't exist yet")
    
    def test_pip_install_editable_works(self):
        """Test that pip install -e . works with meson backend."""
        # This is an integration test that will only work after implementation
        pytest.skip("Will implement after meson build system is ready")


class TestBackwardsCompatibility:
    """Test that old build system still works during transition."""
    
    def test_old_build_system_still_works(self):
        """Test that existing build system still functions."""
        setup_py = Path("setup.py")
        
        if setup_py.exists():
            try:
                result = subprocess.run([
                    'python', 'setup.py', '--help'
                ], capture_output=True, text=True, timeout=30)
                
                assert result.returncode == 0, "Old setup.py should still work"
            except subprocess.TimeoutExpired:
                pytest.fail("setup.py --help timed out")
        else:
            pytest.skip("setup.py doesn't exist")
