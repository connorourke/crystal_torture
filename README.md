[![status](http://joss.theoj.org/papers/c3d8e702ecfee04f16a0ad6f14d96419/status.svg)](http://joss.theoj.org/papers/c3d8e702ecfee04f16a0ad6f14d96419)
[![DOI](https://zenodo.org/badge/139595328.svg)](https://zenodo.org/badge/latestdoi/139595328)
[![PyPI version](https://badge.fury.io/py/crystal-torture.svg)](https://badge.fury.io/py/crystal-torture)
[![build-and-test](https://github.com/connorourke/crystal_torture/actions/workflows/build.yml/badge.svg)](https://github.com/connorourke/crystal_torture/actions/workflows/build.yml)
[![Coverage Status](https://coveralls.io/repos/github/connorourke/crystal_torture/badge.svg?branch=main&service=github)](https://coveralls.io/github/connorourke/crystal_torture?branch=main&service=github)
[![Documentation Status](https://readthedocs.org/projects/crystal-torture/badge/?version=latest)](https://crystal-torture.readthedocs.io/en/latest/?badge=latest)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### **crystal_torture:** 
`crystal_torture` is a Python, Fortran and OpenMP crystal structure analysis module. The module contains a set of classes that enable:

* a crystal structure to be converted into a graph for network analysis. 
* connected clusters of crystal sites (nodes) to be retrieved and output.
* periodicity of connected clusters of crystal sites to be determined.
* relative path tortuosity to traverse a crystal within a connected cluster to be calculated for each site.

Ionic diffusion through crystalline solids depends not only on the dynamics of ions within the crystal, but also the connectivity of the transport network. Understanding how the connectivity of diffusion pathways in crystal structures is affected by changes in chemistry is necessary for understanding how chemical modifications change ionic conductivities, for example the doping of solid electrolytes.

`crystal-torture` provides a [Python API](https://crystal-torture.readthedocs.io/en/latest/) for interrogating network connectivity and diffusion pathways in partially blocked crystal structures. It can be used as a tool for materials scientists to quickly build up network connectivity statistics in order to determine the viability of potential ionic conductors, and how chemical modification affects network connectivity, before the use of more computationally expensive approaches modelling the full dynamics.

## Features

- **Fast Performance**: Fortran extensions with OpenMP parallelisation for computationally intensive operations
- **Fallback Support**: Pure Python implementations available when Fortran extensions unavailable
- **Modern Build System**: Uses meson-python for reliable cross-platform builds
- **Comprehensive Testing**: Extensive test suite covering both Fortran and Python code paths
- **Type Hints**: Modern Python with type annotations for better development experience

## Installation

`crystal_torture` requires Python 3.10 or above.

### From PyPI (Recommended)

For most users, installation from PyPI will provide pre-compiled packages:

```bash
pip install crystal-torture
```

### From Source

Building from source enables Fortran extensions for optimal performance. This requires a Fortran compiler and build tools:

#### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install gfortran build-essential
```

**macOS (with Homebrew):**
```bash
brew install gfortran
```

**Windows:**
Install a Fortran compiler such as MinGW-w64 or use Windows Subsystem for Linux.

#### Installation
```bash
git clone https://github.com/connorourke/crystal_torture
cd crystal_torture
pip install . --use-pep517
```

#### Development Installation
```bash
git clone https://github.com/connorourke/crystal_torture
cd crystal_torture  
pip install ."[dev]" --use-pep517
```

### Fortran Extensions

**Performance Note:** The Fortran extensions provide significant performance improvements for large systems. If Fortran compilation fails, some functions will fall back to Python implementations, while others (like `torture_fort()`) will require using the Python equivalent (`torture_py()`).

To verify Fortran extensions loaded successfully:
```python
from crystal_torture import tort, dist
print(f"Fortran tort available: {tort.tort_mod is not None}")
print(f"Fortran dist available: {dist._DIST_AVAILABLE}")
```

## Quick Start

```python
from crystal_torture.pymatgen_interface import graph_from_file

# Load structure and create graph
graph = graph_from_file("my_structure.cif", rcut=4.0, elements={"Li"})

# Analyse tortuosity (uses Fortran if available)
graph.torture()  # or graph.torture_py() for pure Python

# Get results
percolating_fraction = graph.return_frac_percolating()
for cluster in graph.minimal_clusters:
    print(f"Cluster size: {cluster.size}, Tortuosity: {cluster.tortuosity}")
```

## Tests

`crystal_torture` is automatically tested on each commit via GitHub Actions across Python 3.10-3.13, but tests can be run manually:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=crystal_torture

# Run specific test file
pytest tests/test_node.py -v
```

## Examples

Examples on how to use `crystal_torture` can be found in a Jupyter notebook in the `examples` directory [crystal_torture_examples.ipynb](http://nbviewer.jupyter.org/github/connorourke/crystal_torture/blob/main/examples/crystal_torture_examples.ipynb)

## Documentation

Documentation can be found [here](https://crystal-torture.readthedocs.io/en/latest/)

## Dependencies

### Runtime Dependencies
- `numpy>=1.19.0`
- `pymatgen>=2022.0.0`

### Build Dependencies (for source installation)
- `meson-python>=0.12.0`
- `gfortran` (Fortran compiler)
- `ninja` (build tool)
- OpenMP (optional, for parallelisation)

### Development Dependencies
- `pytest>=6.0`
- `pytest-cov`
- `coverage`
- `ddt`

## Performance

The Fortran extensions with OpenMP provide substantial performance improvements over pure Python implementations, particularly for large crystal structures with many atoms.

## Contributing

### Bug Reports and Feature Requests

If you think you have found a bug, please report it on the [Issue Tracker](https://github.com/connorourke/crystal_torture/issues). This is also the place to propose ideas for new features or ask questions about the design of crystal_torture. Poor documentation is considered a bug, but please be as specific as possible when asking for improvements.

### Code Contributions

We welcome your help in improving and extending the package with your own contributions. This is managed through GitHub pull requests; for external contributions we prefer the "fork and pull" workflow, while core developers use branches in the main repository:

1. First open an [Issue](https://github.com/connorourke/crystal_torture/issues) to discuss the proposed contribution. This discussion might include how the changes fit crystal_torture's scope and a general technical approach.
2. Make your own project fork and implement the changes there. Please keep your code style compliant with PEP8.
3. Add or update tests for your changes.
4. Open a [pull request](https://github.com/connorourke/crystal_torture/pulls) to merge the changes into the main project. A more detailed discussion can take place there before the changes are accepted.

### Development Setup

```bash
git clone https://github.com/connorourke/crystal_torture
cd crystal_torture
pip install ."[dev]" --use-pep517
pytest  # Run tests to verify installation
```

## Citation

If you use `crystal_torture` in your research, please cite:

```bibtex
@article{ORourke2019,
  title = {crystal-torture: A crystal tortuosity module},
  volume = {4},
  ISSN = {2475-9066},
  url = {http://dx.doi.org/10.21105/joss.01306},
  DOI = {10.21105/joss.01306},
  number = {38},
  journal = {Journal of Open Source Software},
  publisher = {The Open Journal},
  author = {O'Rourke,  Conn and Morgan,  Benjamin},
  year = {2019},
  month = jun,
  pages = {1306}
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Version

Current version: 1.2.0

## Changelog

- **v1.2.0**: Modern meson-python build system, improved Fortran integration, Python 3.10+ support
- **v1.1.x**: Previous stable releases with setuptools build system
