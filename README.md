
[![Build Status](https://travis-ci.com/connorourke/crystal_torture.svg?token=nTMqYYEUasQRTBsU6oCc&branch=master)](https://travis-ci.com/connorourke/crystal_torture)
[![Coverage Status](https://coveralls.io/repos/github/connorourke/crystal_torture/badge.svg?branch=master)](https://coveralls.io/github/connorourke/crystal_torture?branch=master)

### **crystal_torture:** 
 `crystal_torture` is a Python, Fortran and OpenMP crystal structure analysis module. The module contains a set of classes
that enable:

* a crystal structure to be converted into a graph for network analysis 
* connected clusters of crystal sites (nodes) to be retrieved and output
* periodicity of connected clusters of crystal sites to be determined
* relative path tortuosity to traverse a crystal within a connected cluster to be calculated for each site
 
 
## Installation

```
pip install crystal_torture
```

or download directly from [GitHub](http://github.com/connorourke/crystal_torture/releases), or clone:

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

