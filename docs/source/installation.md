# Installation

## Requirements

`crystal-torture` requires Python 3.10 or above.

**Core dependencies:**
- `numpy >= 1.19.0`
- `pymatgen >= 2022.0.0`

## Installation from PyPI (Recommended)

Install the latest stable release:

```bash
pip install crystal-torture
```

This installs the package with pre-compiled Fortran extensions for fast tortuosity calculations. If pre-compiled wheels aren't available for your platform, pip will attempt to compile from source.

## Installation from Source

For development or if you need the latest features:

```bash
git clone https://github.com/connorourke/crystal_torture
cd crystal_torture
pip install . --use-pep517
```

### Requirements for Source Installation

**For Fortran extensions (recommended for performance):**
- Fortran compiler (gfortran, ifort, etc.)
- OpenMP support (for parallel calculations)

**On Ubuntu/Debian:**
```bash
sudo apt-get install gfortran
```

**On macOS with Homebrew:**
```bash
brew install gcc
```

**On Windows:**
- Install [MSYS2](https://www.msys2.org/) or use [conda-forge compiler tools](https://conda-forge.org/docs/maintainer/knowledge_base.html#using-centos-7)

## Verify Installation

Test that crystal-torture is properly installed:

```python
import crystal_torture
print(f"crystal-torture version: {crystal_torture.__version__}")

# Test basic functionality
from crystal_torture import graph_from_file
print("✅ Installation successful!")
```

## Performance Notes

- **With Fortran extensions**: Fast parallel tortuosity calculations using OpenMP
- **Python-only fallback**: Automatic fallback if Fortran extensions unavailable
- **No functionality lost**: Pure Python implementations provide identical results

The package automatically detects available extensions and uses the fastest implementation available.

## Troubleshooting

**Import errors:**
- Ensure Python >= 3.10
- Check that numpy and pymatgen are installed: `pip install numpy pymatgen`

**Compilation issues:**
- Install a Fortran compiler (see requirements above)
- The package works without Fortran extensions, just slower

**For help:**
- [GitHub Issues](https://github.com/connorourke/crystal_torture/issues)
- Check existing issues for common problems
