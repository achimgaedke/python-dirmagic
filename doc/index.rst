.. dirmagic documentation master file, created by
   sphinx-quickstart on Thu Apr 13 14:54:29 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-dirmagic's documentation!
###########################################

.. code-block:: ipython

    In [1]: from dirmagic import identify_project

    In [2]: identify_project(".")
    Out[2]: 
    [('IDE', 'Visual Studio Code project'),
     ('packaging', 'python package'),
     ('version control', 'git'),
     ('version control', 'repository')]

Quick intro: :ref:`use-cases`

*Mission:*

``dirmagic`` tells you what type of project/directory structure you're dealing with.

... just like ``file``/``libmagic`` for files.

*Provides:*

* a flexible system to describe directory structures,
* a comprehensive collection of patterns idenitfying projects (e.g. git repositories, python packages, GIS data), and
* an interface & tools to make use of those patterns

*Inspired by:*

* `file command <https://en.wikipedia.org/wiki/File_(command)>`_
* `libmagic <https://www.darwinsys.com/file/>`_ as library of
  `file signatures (aka magic numbers) <https://en.wikipedia.org/wiki/File_format#Magic_number>`_
* `python's binding <https://github.com/ahupp/python-magic>`_ of libmagic
* `rprojroot <https://rprojroot.r-lib.org/>`_
* `pyprojroot <https://github.com/chendaniely/pyprojroot>`_
* ... myself, repeatedly coding some functions to locate data, projects...

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   usecases
   installation
   api_overview
   api_docs
   development
   indices