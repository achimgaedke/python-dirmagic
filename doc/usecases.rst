.. _use-cases:

Use Cases
=========

Find Projects
-------------

Find all directories containing a python package with :py:func:`dirmagic.find_root`
and the python package criterion :py:data:`dirmagic.project_types.is_python_project`:

.. code-block:: ipython

    In [1]: from dirmagic import find_projects, project_types

    In [2]: find_projects("/Users/achim/Code", project_types.is_python_project)
    Out[2]: 
    [PosixPath('/Users/achim/Code/python-dirmagic'),
     PosixPath('/Users/achim/Code/nbconvert'),
     PosixPath('/Users/achim/Code/py-aws-vault')]

Find the Project Root
---------------------

Find the project root in the parent directories with :py:func:`dirmagic.find_root`
and a criterion from :py:mod:`dirmagic.project_types`:

.. code-block:: ipython

    In [1]: from dirmagic import find_root, project_types

    In [2]: find_root("build/html", project_types.is_python_project)
    Out[2]: PosixPath('/Users/achim/Code/python-dirmagic')

    In [3]: find_root("build/html")
    Out[3]: PosixPath('/Users/achim/Code/python-dirmagic')

    In [4]: find_root("build/html", return_reason=True)
    Out[4]: 
    (PosixPath('/Users/achim/Code/python-dirmagic'),
     'contains the directory `.git`')

Commands 3 and 4 are using a default list of criteria as defined in ``pyprojroot``.

Identify Project Types
----------------------

Identify the project types contained in a directory with :py:func:`dirmagic.identify_project`:

.. code-block:: ipython

    In [1]: from dirmagic import identify_project

    In [2]: identify_project(".")
    Out[2]: 
    [('packaging', 'python package'),
     ('version control', 'git'),
     ('version control', 'repository')]

Check Criterion Result
----------------------

Display a result with ``rich``:

.. code-block:: ipython

    In [1]: import dirmagic

    In [2]: dirmagic.project_types.is_git_root.test(".").rich_tree()
    Out[2]: 
    ✔ `git` project type
    └── ✔ OR (1 untested criteria not listed)
        └── ✔ contains the directory `.git`


Custom Criteria
---------------

Build up a custom criterion using the generic criteria classes in
:py:mod:`dirmagic.generic_criteria` and the logical operators
``|`` (or), ``&`` (and) and ``~`` (not).

.. code-block:: ipython

    In [1]: from dirmagic.generic_criteria import HasDir, HasFile, HasFileGlob

    In [2]: is_my_data_tree =  (
        ...:         HasDir("data") &
        ...:         HasFileGlob("data/*.hdf") &
        ...:         HasFile("metadata.json") &
        ...:         ~ HasFile(".ignore")
        ...:     )

    In [3]: is_my_data_tree.rich_tree()
    Out[3]: 
    AND
    ├── contains the directory `data`
    ├── has a file matching `data/*.hdf`
    ├── has a file `metadata.json`
    └── NOT
        └── has a file `.ignore`

The criterion can be used with :py:func:`dirmagic.find_projects` or
:py:func:`dirmagic.find_root` - just as above.

Check Criterion
---------------

Display a criterion with ``rich``:

.. code-block:: ipython

    In [1]: import dirmagic

    In [2]: dirmagic.project_types.is_vcs_root.rich_tree()
    Out[2]: 
    `repository` project type
    └── OR
        ├── `git` project type
        │   └── OR
        │       ├── contains the directory `.git`
        │       └── has a file `.git` and file contains a line matching the regular expression `^gitdir: `
        └── `subversion` project type
            └── contains the directory `.svn`
