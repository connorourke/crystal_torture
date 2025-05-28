project('crystal_torture', 'fortran',
  version: '1.2.0',
  license: 'MIT',
  meson_version: '>= 0.64.0'
)

# =============================================================================
# IMPORTANT NOTES ON BUILD SYSTEM ISSUES
# =============================================================================
#
# This project uses meson-python for building Fortran extensions. During 
# development, we encountered several meson-python maturity issues:
#
# 1. EDITABLE INSTALLS: 
#    - Editable installs (pip install -e .) are unreliable across all Python versions
#    - Extensions build but fail to load due to temporary build environment cleanup
#    - Workaround: Use regular installs (pip install .) for development
#
# 2. CI ENVIRONMENT COMPATIBILITY:
#    - Python 3.11: Extensions build and package correctly in CI ✅
#    - Python 3.10/3.12: Extensions build but fail to package properly in CI ❌
#    - Same versions work fine locally with regular installs
#    - Issue appears to be CI environment + meson-python interaction
#
# 3. PLATFORM DIFFERENCES:
#    - macOS: Regular installs work consistently
#    - Linux CI: Only Python 3.11 packages extensions reliably
#    - Extension names: Platform-specific (e.g., _tort.cpython-311-x86_64-linux-gnu.so)
#
# 4. CURRENT LIMITATIONS:
#    - CI tests only Python 3.11 due to packaging issues
#    - Users can still try other Python versions locally (often works)
#    - Fortran functionality is fully working when extensions package correctly
#
# 5. FUTURE IMPROVEMENTS:
#    - Consider switching to scikit-build + CMake for broader Python support
#    - Monitor meson-python maturity improvements
#    - Investigate CI environment differences causing packaging failures
#
# If you encounter similar issues:
# - Try regular install instead of editable: pip install .
# - Check if extensions exist in build directory but not in package
# - Consider using Python 3.11 as the most reliable version
# - Report meson-python packaging issues to their project
#
# =============================================================================

# Find Python installation and dependencies
py = import('python').find_installation(pure: false)
py_dep = py.dependency()
np_dep = dependency('numpy')

# Configure Fortran compiler
fc = meson.get_compiler('fortran')

# Set optimised Fortran compilation flags
fortran_args = ['-O3', '-fPIC']

# Configure OpenMP support for parallel processing
openmp_dep = dependency('openmp', required: false)
if openmp_dep.found()
  fortran_args += ['-fopenmp']
  message('OpenMP support enabled')
else
  message('OpenMP not found - building without OpenMP')
endif

# Define Fortran source files
tort_sources = files(
  'crystal_torture/tort.f90',
  'crystal_torture/tort_c_interface.f90'
)

dist_sources = files('crystal_torture/dist.f90')

# Build Python extensions and install them in the package directory
# Note: The 'subdir' parameter is crucial for meson-python to install
# extensions in the correct location within the Python package.
# However, this has proven unreliable in CI environments for Python != 3.11
tort_ext = py.extension_module('_tort',
  tort_sources,
  fortran_args: fortran_args,
  dependencies: [openmp_dep],
  install: true,
  subdir: 'crystal_torture'  # Install into crystal_torture package directory
)

dist_ext = py.extension_module('libdist',
  dist_sources,
  fortran_args: fortran_args,
  dependencies: [openmp_dep],
  install: true,
  subdir: 'crystal_torture'  # Install into crystal_torture package directory
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

# Display build configuration summary
summary({
  'Fortran Compiler': fc.get_id(),
  'Python Installation': py.full_path(),
  'NumPy Available': np_dep.found(),
  'OpenMP Support': openmp_dep.found(),
  'Extensions Built': ['_tort', 'libdist'],
  'Build System Note': 'meson-python has known CI packaging issues on Python != 3.11',
}, section: 'Crystal Torture Build Configuration')
