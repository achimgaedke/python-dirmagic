# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os.path

sys.path.append(os.path.abspath(f"{__file__}/../.."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "python-dirmagic"
copyright = "2023, Achim Gädke"
author = "Achim Gädke"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
    "IPython.sphinxext.ipython_directive",
    "IPython.sphinxext.ipython_console_highlighting",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Options for autodoc ------------------------------------------------------

autodoc_typehints = "both"
autodoc_mock_imports = ["rich"]

# -- Options for intersphinx --------------------------------------------------


intersphinx_mapping = {
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "python": ("https://docs.python.org/3/", None),
    "rich": ("https://rich.readthedocs.io/en/stable/", None),
}

intersphinx_disabled_reftypes = ["*"]
