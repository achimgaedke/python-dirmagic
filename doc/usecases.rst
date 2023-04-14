Use Cases
=========

Find all directories containing a python package

.. code-block:: python

    from dirmagic import find_projects, project_types

    find_projects("~/Code", project_types.python_package)

Find the DVC root in your parent directories

.. code-block:: python

    from dirmagic import find_root, project_types

    find_root(
        "~/Code/DS-Project/somewhere/in/it",
        project_types.dvc_repository
        )

Returns ````

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