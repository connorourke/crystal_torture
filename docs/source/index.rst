crystal-torture: A crystal tortuosity module
============================================

|Build Status| |Test Coverage|

`crystal-torture` is a Python, Fortran, and OpenMP module for the analysis of diffusion networks in crystal structures. The module contains a set of classes that enable:

* a crystal structure to be converted into a graph for network analysis
* connected clusters of crystal sites (nodes) to be retrieved and output
* periodicity of connected clusters of crystal sites to be determined
* relative path tortuosity to traverse a crystal within a connected cluster to be calculated for each site

Ionic diffusion through crystalline solids depends not only on the dynamics of ions within the crystal, but also the connectivity of the transport network. Understanding how the connectivity of diffusion pathways in crystal structures is affected by changes in chemistry is necessary for understanding how chemical modifications change ionic conductivities, for example the doping of solid electrolytes.

`crystal-torture` provides a Python API for interrogating network connectivity and diffusion pathways in partially blocked crystal structures. It can be used as a tool for materials scientists to quickly build up network connectivity statistics to determine the viability of potential ionic conductors, and how chemical modification affects network connectivity, before the use of more computationally expensive approaches modelling the full dynamics.

Features
--------

* **Fast Performance**: Fortran extensions with OpenMP parallelisation for computationally intensive operations
* **Fallback Support**: Pure Python implementations available when Fortran extensions unavailable  
* **Modern Build System**: Uses meson-python for reliable cross-platform builds
* **Comprehensive Testing**: Extensive test suite covering both Fortran and Python code paths
* **Type Hints**: Modern Python with type annotations for better development experience

Installation
------------

`crystal-torture` requires Python 3.10 or above.

From PyPI::

    pip install crystal-torture

From source (requires Fortran compiler)::

    git clone https://github.com/connorourke/crystal_torture
    cd crystal_torture
    pip install . --use-pep517

Documentation is `here <modules.html>`__.

Examples are provided in a Jupyter notebook `here <http://nbviewer.jupyter.org/github/connorourke/crystal_torture/blob/master/examples/crystal_torture_examples.ipynb>`__

Source code is available as a git repository at https://github.com/connorourke/crystal_torture.

Citation
--------

If you use `crystal-torture` in your research, please cite:

O'Rourke, C., & Morgan, B. J. (2019). crystal-torture: A crystal tortuosity module. *Journal of Open Source Software*, 4(38), 1306. https://doi.org/10.21105/joss.01306

Tests
-----

Automated testing of the latest commit happens via `GitHub Actions <https://github.com/connorourke/crystal_torture/actions>`__.

Manual tests can be run using::

    pytest

Or with coverage::

    pytest --cov=crystal_torture

The code has been tested with Python versions 3.10, 3.11, 3.12, and 3.13.

.. toctree::
   :maxdepth: 4
   :caption: Documentation:

   modules

Index
=====

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |Build Status| image:: https://github.com/connorourke/crystal_torture/actions/workflows/build.yml/badge.svg
   :target: https://github.com/connorourke/crystal_torture/actions/workflows/build.yml
.. |Test Coverage| image:: https://coveralls.io/repos/github/connorourke/crystal_torture/badge.svg?branch=master
   :target: https://coveralls.io/github/connorourke/crystal_torture?branch=master
