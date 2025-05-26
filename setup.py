"""Setup script for crystal_torture package."""
import os
import sys
import subprocess
from pathlib import Path

# Only import setuptools components that we need
from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.install import install


def build_fortran_extensions():
    """Build the Fortran extensions using the original build script."""
    # Change to crystal_torture directory for compilation
    original_dir = os.getcwd()
    crystal_torture_dir = Path(__file__).parent / "crystal_torture"
    
    try:
        os.chdir(crystal_torture_dir)
        
        # Make build script executable and run it
        build_script = Path("build_tort.sh")
        if build_script.exists():
            # Make executable
            os.chmod(build_script, 0o755)
            # Run the build script
            result = subprocess.run(["bash", str(build_script)], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Build script failed with return code {result.returncode}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                raise RuntimeError("Failed to build Fortran extensions")
        else:
            print("Warning: build_tort.sh not found. Trying manual build...")
            _manual_build()
            
    except Exception as e:
        print(f"Error building Fortran extensions: {e}")
        print("Make sure you have gfortran and f90wrap installed.")
        # Don't raise here - allow installation to continue for development
    finally:
        os.chdir(original_dir)


def _manual_build():
    """Manually build the extensions if build script is missing."""
    try:
        # Build dist extension
        subprocess.run([
            "f2py", "-c", "--opt=-O3", "--f90flags=-fopenmp",
            "-lgomp", "-m", "dist", "dist.f90"
        ], check=True)
        
        # Compile tort.f90 to object file
        subprocess.run([
            "gfortran", "-O3", "-Wall", "-c", "-fopenmp", 
            "-fPIC", "tort.f90"
        ], check=True)
        
        # Build tort extension with f90wrap
        subprocess.run([
            "f2py-f90wrap", "-c", "--opt=-O3", 
            "--f90flags=-fopenmp", "-lgomp", 
            "-m", "_tort", "f90wrap_tort.f90", "tort.o"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Manual build failed: {e}")
        raise


class CustomBuildPy(build_py):
    """Custom build_py to build Fortran extensions."""
    
    def run(self):
        # Build Fortran extensions first
        build_fortran_extensions()
        # Then run normal build_py
        super().run()


class CustomDevelop(develop):
    """Custom develop command to build Fortran extensions."""
    
    def run(self):
        # Build Fortran extensions first
        build_fortran_extensions()
        # Then run normal develop
        super().run()


class CustomInstall(install):
    """Custom install command to build Fortran extensions."""
    
    def run(self):
        # Build Fortran extensions first
        build_fortran_extensions()
        # Then run normal install
        super().run()


def check_fortran_compiler():
    """Check if gfortran is available."""
    try:
        subprocess.run(["gfortran", "--version"], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    """Main setup function."""
    # Check for Fortran compiler
    if not check_fortran_compiler():
        print("Warning: gfortran not found. Fortran extensions may not build.")
        print("Please install gfortran to enable full functionality.")
    
    # Read version from version.py
    version_file = Path(__file__).parent / "crystal_torture" / "version.py"
    version_globals = {}
    exec(version_file.read_text(), version_globals)
    version = version_globals["__version__"]
    
    setup(
        version=version,
        cmdclass={
            "build_py": CustomBuildPy,
            "develop": CustomDevelop,
            "install": CustomInstall,
        },
    )


if __name__ == "__main__":
    main()
