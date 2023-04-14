.. _use-cases:

Use Cases
=========

Find Projects
-------------

Find all directories containing a python package with :py:func:`dirmagic.find_root`
and the python package criterion :py:data:`dirmagic.project_types.is_python_project`:

.. code-block:: python

    from dirmagic import find_projects, project_types

    find_projects("/home/me/Code", project_types.is_python_project)

Returns ``[pathlib.Path("/home/me/Code/py-Project1"), pathlib.Path("/home/me/Code/py-Project2"), ...]``.

Find Project Root
-----------------

Find the DVC root in your parent directories with :py:func:`dirmagic.find_root`
and a criterion from :py:mod:`dirmagic.project_types`:

.. code-block:: python

    from dirmagic import find_root, project_types

    find_root(
        "/home/me/Code/DS-Project/somewhere/in/it",
        project_types.dvc_repository
        )

Returns ``pathlib.Path("/home/me/Code/DS-Project")``.

Identify Project Type
---------------------

Identify the project types contained in a directory with :py:func:`dirmagic.identify_project`:

.. code-block:: python

    from dirmagic import identify_project

    identify_project(".")

Returns: 

.. code-block:: python

    [
        ('IDE', 'Visual Studio Code project'),
        ('packaging', 'python package'),
        ('version control', 'git'),
        ('version control', 'repository')
    ]


Use A Custom Criterion
----------------------

Build up a custom criterion using the generic criteria classes in
:py:mod:`dirmagic.generic_criteria` and the logical operators
``|`` (or), ``&`` (and) and ``~`` (not).

.. code-block:: python

    from dirmagic import find_projects
    from dirmagic.generic_criteria import HasDir, HasFile, HasFileGlob

    is_my_data_tree =  (
        HasDir("data") &
        HasFileGolb("data/*.hdf") &
        HasFile("metadata.json") &
        ~ HasFile(".ignore")
    )
    find_projects("/data/", is_my_data_tree, max_depth=10)