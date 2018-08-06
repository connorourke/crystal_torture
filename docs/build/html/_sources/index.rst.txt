
crystal_torture:  a crystal tortuosity module
=============================================

|Build Status| |Test Coverage|

`crystal_torture` is a Python, Fortran and OpenMP crystal structure analysis module. The module contains a set of classes that enable:

* a crystal structure to be converted into a graph for network analysis,
* connected clusters of crystal sites (nodes) to be retrieved and output
* periodicity of connected clusters of crystal sites to be determined
* relative path tortuosity to traverse a crystal within a connected cluster to be calculated for each site


Documentation is  `here <modules.html>`__.

Examples are provided in a Jupyter notebook `here <http://nbviewer.jupyter.org/github/connorourke/crystal_torture/blob/master/examples/crystal_torture_examples.ipynb>`__

Source code is available as a git repository at https://github.com/connorourke/crystal_torture.


Tests
-----

Automated testing of the latest commit happens
`here <https://travis-ci.org/connorourke/crystal_torture>`__.

Manual tests can be run using

::

    python -m unittest discover

The code has been tested with Python versions 3.5 and above.


.. toctree::
   :maxdepth: 4
   :caption: Documentation:

   modules

Index
=====

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |Build Status| image:: https://travis-ci.com/connorourke/crystal_torture.svg?token=nTMqYYEUasQRTBsU6oCc&branch=master
   :target: https://travis-ci.com/connorourke/crystal_torture
.. |Test Coverage| image:: https://coveralls.io/repos/github/connorourke/crystal_torture/badge.svg?branch=master
   :target: https://coveralls.io/github/connorourke/crystal_torture?branch=master

