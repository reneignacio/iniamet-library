# -- Configuración de Sphinx para INIAMET --
import os
import sys

sys.path.insert(0, os.path.abspath('../../src'))

project = 'INIAMET'
copyright = '2025-2026, René Sepúlveda'
author = 'René Sepúlveda'
version = '0.2.0'
release = '0.2.0'
language = 'es'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
    'myst_parser',
]

# Napoleon
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# Autodoc
autodoc_member_order = 'bysource'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# HTML
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 3,
    'collapse_navigation': False,
}
html_static_path = ['_static']

# Source
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
