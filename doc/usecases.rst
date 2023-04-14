.. _use-cases:

Use Cases
=========

Find all directories containing a python package

.. code-block:: python

    from dirmagic import find_projects, project_types

    find_projects("/home/me/Code", project_types.python_package)

Returns ``[pathlib.Path("/home/me/Code/py-Project1"), pathlib.Path("/home/me/Code/py-Project2"), ...]``.

Find the DVC root in your parent directories

.. code-block:: python

    from dirmagic import find_root, project_types

    find_root(
        "/home/me/Code/DS-Project/somewhere/in/it",
        project_types.dvc_repository
        )

Returns ``pathlib.Path("/home/me/Code/DS-Project")``.

Identify project type contained in directory:

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