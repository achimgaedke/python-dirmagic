.. dirmagic documentation master file, created by
   sphinx-quickstart on Thu Apr 13 14:54:29 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to dirmagic's documentation!
====================================

*Can't wait, get started?*


.. code-block:: shell

   pip install git+https://github.com/achimgaedke/dirmagic.git

Supports python>=3.7

.. code-block:: python

   import dirmagic

   data_directories = dirmagic.find_projects("~/data-mirror/",  XXX_pattern)

*Mission:*

Just like filemagic but for directories, it tells you what type of
project/directory structure you're dealing with.

*Provides:*

* a powerful pattern matching system to describe directory structures,
* a comprehensive collection of patterns idenitfying projects (e.g. git repositories, python packages, GIS data), and
* an interface & tools to make use of those patterns

*Inspired by:*

* `libmagic <https://www.darwinsys.com/file/>`_ and the ``file`` command
* `python's binding <https://github.com/ahupp/python-magic>`_
* `rprojroot <https://rprojroot.r-lib.org/>`_
* `pyprojroot <https://github.com/chendaniely/pyprojroot>`_

... repeatedly trying to find data, projects, subprojects programatically

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   usecases
   project_types
   api_docs
   development

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
