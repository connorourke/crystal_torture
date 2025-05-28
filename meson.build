project('crystal_torture', 'fortran',
  version: '1.2.0',
  license: 'MIT',
  meson_version: '>= 0.64.0'
)

# =============================================================================
# CRYSTAL TORTURE BUILD CONFIGURATION
# =============================================================================
#
# Builds Fortran extensions using meson-python for tortuosity analysis.
#
# SUPPORTED: Python 3.10, 3.11, 3.12, 3.13
# INSTALLATION: pip install . --use-pep517
#
# =============================================================================

# Find Python installation and dependencies
py = import('python').find_installation(pure: false)
py_dep = py.dependency()
np_dep = dependency('numpy')

# Configure Fortran compiler
fc = meson.get_compiler('fortran')
fortran_args = ['-O3', '-fPIC']

# Configure OpenMP support
openmp_dep = dependency('openmp', required: false)
if openmp_dep.found()
  fortran_args += ['-fopenmp']
  message('OpenMP support enabled')
else
  message('Building without OpenMP')
endif

# Define Fortran source files
tort_sources = files(
  'crystal_torture/tort.f90',
  'crystal_torture/tort_c_interface.f90'
)

dist_sources = files('crystal_torture/dist.f90')

# Build Python extensions
tort_ext = py.extension_module('_tort',
  tort_sources,
  fortran_args: fortran_args,
  dependencies: [openmp_dep],
  install: true,
  subdir: 'crystal_torture'
)

dist_ext = py.extension_module('libdist',
  dist_sources,
  fortran_args: fortran_args,
  dependencies: [openmp_dep],
  install: true,
  subdir: 'crystal_torture'
)

# Install Python source files
python_sources = [
  'crystal_torture/__init__.py',
  'crystal_torture/node.py',
  'crystal_torture/cluster.py', 
  'crystal_torture/graph.py',
  'crystal_torture/minimal_cluster.py',
  'crystal_torture/pymatgen_interface.py',
  'crystal_torture/pymatgen_doping.py',
  'crystal_torture/tort.py',
  'crystal_torture/dist.py',
  'crystal_torture/version.py'
]

py.install_sources(python_sources, subdir: 'crystal_torture')

# Build summary
summary({
  'Fortran Compiler': fc.get_id(),
  'Python Version': py.language_version(),
  'NumPy Available': np_dep.found(),
  'OpenMP Support': openmp_dep.found(),
}, section: 'Crystal Torture Build Configuration')
