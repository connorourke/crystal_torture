# -*- coding: utf-8 -*-
"""Configuration file for the Sphinx documentation builder."""

import os
import sys

# Add project to path
sys.path.insert(0, os.path.abspath('../../'))

# Import version from package
from crystal_torture.version import __version__

# -- Project information -----------------------------------------------------
project = 'crystal_torture'
copyright = '2024, Conn O\'Rourke'
author = 'Conn O\'Rourke'

# Version from package
version = __version__
release = __version__

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # Google-style docstrings
    'sphinx.ext.viewcode',  # Source code links
    'sphinx.ext.githubpages',
    'myst_nb',             # Jupyter notebook support (includes myst_parser)
]

# Source file extensions
source_suffix = {
    '.rst': None,
    '.md': None,
    '.ipynb': None,
}

# Master doc
master_doc = 'index'

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False

# MyST settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_image",
]

# Templates and static files
templates_path = ['_templates']
html_static_path = ['_static']
exclude_patterns = []

# Language
language = 'en'

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'

# Alabaster theme options
html_theme_options = {
    'github_user': 'connorourke',
    'github_repo': 'crystal_torture',
    'description': 'A crystal tortuosity module',
    'fixed_sidebar': True,
}

# Sidebar configuration
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
    ]
}

# Output file base name for HTML help builder
htmlhelp_basename = 'crystal_torturedoc'

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {}

latex_documents = [
    (master_doc, 'crystal_torture.tex', 'crystal\\_torture Documentation',
     'Conn O\'Rourke', 'manual'),
]

# -- Options for manual page output ------------------------------------------
man_pages = [
    (master_doc, 'crystal_torture', 'crystal_torture Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    (master_doc, 'crystal_torture', 'crystal_torture Documentation',
     author, 'crystal_torture', 'One line description of project.',
     'Miscellaneous'),
]
