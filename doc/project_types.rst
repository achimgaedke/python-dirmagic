Project Type Criteria
=====================

This module contains a variety of directory criteria describing project
types.

Each :py:class:`dirmagic.core_criteria.ProjectType` provides a
name and a category for the project type along with the criterion describing
the expected directory structure.

By default :py:func:`dirmagic.identify_project` uses all project types in this
module to determine matching the project types.

Please see the development section for instructions on how to contribute
to this collection.

.. automodule:: dirmagic.project_types
    :members:
    :synopsis: Predfined criteria for detecting known (project) directory types
