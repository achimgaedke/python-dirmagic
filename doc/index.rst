.. dirmagic documentation master file, created by
   sphinx-quickstart on Thu Apr 13 14:54:29 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-dirmagic's documentation!
===========================================

*Can't wait, get started?*

.. code-block:: shell

   pip install git+https://github.com/achimgaedke/python-dirmagic.git

Supports python>=3.7, and then move to :ref:`use-cases`.

*Mission:*

``dirmagic`` tells you what type of project/directory structure you're dealing with.

... just like ``file``/``libmagic`` for files.

*Provides:*

* a flexible system to describe directory structures,
* a comprehensive collection of patterns idenitfying projects (e.g. git repositories, python packages, GIS data), and
* an interface & tools to make use of those patterns

*Inspired by:*

* `file command <https://en.wikipedia.org/wiki/File_(command)>`_`
* `libmagic <https://www.darwinsys.com/file/>`_ as library of "magic numbers"
* `python's binding <https://github.com/ahupp/python-magic>`_ of libmagic
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
