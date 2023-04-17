Development
===========

Source code repository and issue tracker at `github
<https://github.com/achimgaedke/python-dirmagic/>`_.

At the moment:

One-man show using a MacBook with VS Code, mainly python 3.11,
using some auto-formatting(black), linting (mypy,flake), testing (pytest)

Compatibility:

Python 3.7 ... 3.12 on all CPython platforms.

Optional dependencies:

* `rich <https://rich.readthedocs.io/en/latest/>`_ for fancy terminal output
  (display reason for matching)

Useful commands
---------------

For local development

Create a development environment:

.. code-block:: shell

    mamba env create -f dev_environment.yml
    conda activate dirmagic-dev-env

Change python version of the development enviroment:

.. code-block:: shell

    mamba install -n dirmagic-dev-env "python=3.9"

Build documentation:

.. code-block:: shell

    sphinx-build doc build/html

Build distribution:

.. code-block:: shell

    python -m build

Reformat python files in-place:

.. code-block:: shell

    python -m black dirmagic tests

Test and lint project:

.. code-block:: shell

    python -m pytest --cov-report term-missing --cov=dirmagic  tests
    python -m mypy dirmagic tests
    python -m flake dirmagic tests
    python -m black --check dirmagic tests

Or use ``tox``:

.. code-block:: shell

    tox -f <what>

with ``<what>`` as one of ``test,lint,type,coverage,format``.

Contributing
------------

* Add a criterion defining a project type
* Advocate for a use case
* Improve documentation
* Extend the set of criteria to define project types
* Improve the code (correctness, performance or capability)

What the project is not
-----------------------

* An alternative to package data/resource locators for installed packages like
  ``pkgutil.get_data``.
* An in-depth validation of a project's data.

Project Maturity
----------------

Inception state, answering the question: *Will this resonate with a reasonably
broad community?*

Aim for a 0.1 release with a preliminary interface, continue towards 1.0 using
semantic versioning.
