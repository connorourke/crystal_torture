#!/usr/bin/env python3
"""
Debug script to understand what's happening with meson build.
Run this to see detailed output.
"""
import subprocess
import tempfile
from pathlib import Path
import os

def debug_meson_build():
    """Debug the meson build process step by step."""
    print("=== Debugging Meson Build Process ===")
    
    # Check if meson is available
    try:
        result = subprocess.run(['meson', '--version'], capture_output=True, text=True)
        print(f"✅ Meson version: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Meson not found!")
        return
    
    # Check if gfortran is available
    try:
        result = subprocess.run(['gfortran', '--version'], capture_output=True, text=True)
        print(f"✅ Fortran compiler available")
        print(f"   First line: {result.stdout.split()[0:4]}")
    except FileNotFoundError:
        print("❌ gfortran not found!")
        return
    
    # Create a temporary build directory
    with tempfile.TemporaryDirectory() as temp_dir:
        build_dir = Path(temp_dir) / "debug_build"
        print(f"📁 Using build directory: {build_dir}")
        
        # Try meson setup (no verbose flag for setup)
        print("\n=== Running meson setup ===")
        setup_result = subprocess.run([
            'meson', 'setup', str(build_dir)
        ], capture_output=True, text=True, cwd='.')
        
        print(f"Setup return code: {setup_result.returncode}")
        print(f"Setup stdout:\n{setup_result.stdout}")
        if setup_result.stderr:
            print(f"Setup stderr:\n{setup_result.stderr}")
        
        if setup_result.returncode != 0:
            print("❌ Meson setup failed!")
            return
        
        # Try meson compile with verbose output
        print("\n=== Running meson compile ===")
        build_result = subprocess.run([
            'meson', 'compile', '-C', str(build_dir), '-v'
        ], capture_output=True, text=True)
        
        print(f"Build return code: {build_result.returncode}")
        print(f"Build stdout:\n{build_result.stdout}")
        if build_result.stderr:
            print(f"Build stderr:\n{build_result.stderr}")
        
        # List all files created in build directory
        print(f"\n=== Files in build directory ===")
        if build_dir.exists():
            for item in build_dir.rglob("*"):
                if item.is_file():
                    print(f"  {item.relative_to(build_dir)} ({item.stat().st_size} bytes)")
        
        # Specifically look for shared libraries (platform-specific)
        import platform
        if platform.system() == "Darwin":  # macOS
            shared_files = list(build_dir.rglob("*.dylib"))
        elif platform.system() == "Windows":
            shared_files = list(build_dir.rglob("*.dll"))
        else:  # Linux and others
            shared_files = list(build_dir.rglob("*.so"))
            
        print(f"\n=== Shared libraries found: {len(shared_files)} ===")
        for shared_file in shared_files:
            print(f"  {shared_file}")
        
        # Look for static libraries too
        static_files = list(build_dir.rglob("*.a"))
        print(f"\n=== Static libraries found: {len(static_files)} ===")
        for static_file in static_files:
            print(f"  {static_file}")
        
        # Look for any compiled objects
        compiled_files = (
            list(build_dir.rglob("*.o")) + 
            list(build_dir.rglob("*.a")) + 
            list(build_dir.rglob("*.dylib")) +
            list(build_dir.rglob("*.dll"))
        )
        print(f"\n=== Compiled objects found: {len(compiled_files)} ===")
        for compiled_file in compiled_files:
            print(f"  {compiled_file}")

if __name__ == "__main__":
    debug_meson_build()
