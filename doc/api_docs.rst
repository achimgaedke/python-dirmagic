API documentation
=================

Top Level Functions
-------------------

These functions make use of the criteria, e.g. the predefined project types.

.. autofunction:: dirmagic.find_root

.. autofunction:: dirmagic.find_projects

.. autofunction:: dirmagic.identify_project

Generic Criteria
----------------

Define the expected entries and their properties using criterion classes.

These classes are used to define project types and directory patterns.

.. automodule:: dirmagic.generic_criteria
    :members:
    :undoc-members:

Core Criteria
-------------

This module provides the abstract criteria and operations on those,
like ``&``, ``|`` and ``~``.
The test result object is defined here as well.

.. automodule:: dirmagic.core_criteria
    :members:
    :undoc-members:
