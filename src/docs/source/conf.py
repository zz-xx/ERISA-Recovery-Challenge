# -- Connect Sphinx to the Django project -----------------------
import os
import sys
import django

# Add the project's 'src' directory to the Python path
sys.path.insert(0, os.path.abspath('../..'))

# Set up the Django environment
os.environ['DJANGO_SETTINGS_MODULE'] = 'erisa_project.settings'
django.setup()

# -- Project information -----------------------------------------------------
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ERISA Recovery Challenge'
copyright = '2025, yashr'
author = 'yashr'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # Automatically generate docs from docstrings
    'sphinx.ext.viewcode', # Add links to the source code from the docs
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'insegel'
html_static_path = ['_static']
