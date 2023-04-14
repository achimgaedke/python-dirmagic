Development
===========

At the moment: One-man show using a MacBook with VS Code

Using some auto-formatting, linting, testing (pytest)

Compatibility:

Python 3.7 ... 3.11 on all CPython platforms

Optional dependencies

* `python-magic <https://github.com/ahupp/python-magic>`_ for a file type criterion
* `rich <https://rich.readthedocs.io/en/latest/>`_ for fancy terminal output (display reason for matching)

Useful commands
---------------

Create a development environment

.. code-block:: shell

    mamba env create -f dev_environment.yml
    conda activate dirmagic-dev-env

Change python version of the development enviroment:

.. code-block:: shell

    mamba install -n dirmagic-dev-env "python=3.9"

Build documentation:

.. code-block:: shell

    sphinx-build doc build

Test project:

.. code-block: shell

    python -m pytest --cov-report term-missing --cov=dirmagic  tests
    python -m mypy dirmagic

Todo:

* linting,
* testing,
* coverage of tests and documentation,
* build python packages (whl, ...),
* upload documentation, e.g. to rtd
* upload package to pypi
* setup a conda project

and all this also with github supported CI pipelines.

Contributing
------------

* Add a pattern defining project directory
* Advocate for a use case
* Improve documentation
* Improve the code (correctness, performance or capability)

What the project is not
-----------------------

* An alternative to package data/resource locators for installed packages like
  ``pkgutil.get_data``.
* A full validation of the project's data.

Project Maturity
----------------

Inception state, answering the question: *Will this resonate with a reasonably
broad community?*

Aim for a 0.1 release with a preliminary interface, continue towards 1.0 using semantic versioning.