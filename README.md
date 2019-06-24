
[![status](http://joss.theoj.org/papers/c3d8e702ecfee04f16a0ad6f14d96419/status.svg)](http://joss.theoj.org/papers/c3d8e702ecfee04f16a0ad6f14d96419)
[![DOI](https://zenodo.org/badge/139595328.svg)](https://zenodo.org/badge/latestdoi/139595328)
[![PyPI version](https://badge.fury.io/py/crystal-torture.svg)](https://badge.fury.io/py/crystal-torture)
[![Build Status](https://travis-ci.com/connorourke/crystal_torture.svg?token=nTMqYYEUasQRTBsU6oCc&branch=master)](https://travis-ci.com/connorourke/crystal_torture)
[![Coverage Status](https://coveralls.io/repos/github/connorourke/crystal_torture/badge.svg?branch=master)](https://coveralls.io/github/connorourke/crystal_torture?branch=master)
[![Documentation Status](https://readthedocs.org/projects/crystal-torture/badge/?version=latest)](https://crystal-torture.readthedocs.io/en/latest/?badge=latest)
[![Python 3.5](https://img.shields.io/badge/python-3.5-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-360/)


### **crystal_torture:** 
 `crystal_torture` is a Python, Fortran and OpenMP crystal structure analysis module. The module contains a set of classes that enable:

* a crystal structure to be converted into a graph for network analysis. 
* connected clusters of crystal sites (nodes) to be retrieved and output.
* periodicity of connected clusters of crystal sites to be determined.
* relative path tortuosity to traverse a crystal within a connected cluster to be calculated for each site.

Ionic diffusion through crystalline solids depends not only on the dynamics of ions within the crystal, but also the connectivity of the transport network. Understanding how the connectivity of diffusion pathways in crystal structures is affected by changes in chemistry is necessary for understanding how chemical modifications change ionic conductivities, for example the doping of solid electrolytes.

`crystal-torture` provides a [Python API](https://crystal-torture.readthedocs.io/en/latest/) for interrogating network connectivity and diffusion pathways in partially blocked crystal structures. It can be used as a tool for materials scientists to quickly build up network connectivity statistics in order to determine the viability of potential ionic conductors, and how chemical modification affects network connectivity, before the use of more computationally expensive approaches modelling the full dynamics.

 
## Installation

`crystal_torture` requires python 3.5 and above. To install do:

```
pip install crystal_torture
```

or download directly from [GitHub](https://github.com/connorourke/crystal_torture/releases/latest), or clone:

```
 git clone https://github.com/connorourke/crystal_torture
```

 and install

```
cd crystal_torture
python setup.py install
```

## Tests

`crystal_torture` is automatically tested on each commit [here](http://travis-ci.org/connorourke/crystal_torture), but the tests can be manually run:

```
python -m unittest discover
```

## Examples
Examples on how to use `crystal_torture` can be found in a Jupyter notebook in the `examples` directory [crystal_torture_examples.ipynb](http://nbviewer.jupyter.org/github/connorourke/crystal_torture/blob/master/examples/crystal_torture_examples.ipynb)


## Documentation
Documentation can be found  [here](https://crystal-torture.readthedocs.io/en/latest/)


## Contributing

### Bugs reports and feature requests

If you think you have found a bug, please report it on the [Issue Tracker](https://github.com/connorourke/crystal_torture/issues). This is also the place to propose ideas for new features or ask questions about the design of pyscses. Poor documentation is considered a bug, but please be as specific as possible when asking for improvements.

### Code contributions

We welcome your help in improving and extending the package with your own contributions. This is managed through GitHub pull requests; for external contributions we prefer the "fork and pull" workflow, while core developers use branches in the main repository:

- First open an [Issue](https://github.com/conn_orourke/crystal_torture/issues) to discuss the proposed contribution. This discussion might include how the changes fit pyscses' scope and a general technical approach.
- Make your own project fork and implement the changes there. Please keep your code style compliant with PEP8.
- Open a [pull request](https://github.com/connorourke/crystal_torture/pulls) to merge the changes into the main project. A more detailed discussion can take place there before the changes are accepted.


