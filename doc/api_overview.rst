API Overview
============

Top level namespace:

- Functions utilising the criteria
- Criteria grouped into 3 modules

    - Generic Criteria, like :py:class:`dirmagic.generic_criteria.HasFile`
    - Pattern Criteria, like :py:class:`dirmagic.pattern_criteria.AnyMatchCriterion`
    - Project Types, like :py:class:`dirmagic.project_types.is_python_project`

- The base classes for criteria and the result of a test.

Any criterion can be used on its own with its :py:meth:`dirmagic.core_criteria.Criterion.test`
method, returning a :py:class:`dirmagic.core_criteria.CriterionResult` object.
This object is true if the test criterion is successful on the directory
specified. It also contains a detailed report on the test result.

Generic Criteria
----------------

Module :py:mod:`dirmagic.generic_criteria`

Define the expected entries and their properties using criterion classes.

These classes are used to define project types and directory patterns.

Generic criteria can be combined using the operators ``&``, ``|`` and negated
with ``~``. Most generic criteria can be used within
:py:class:`dirmagic.pattern_criteria.AnyMatchCriterion` or
:py:class:`dirmagic.pattern_criteria.AllMatchCriterion` to build up complex
criteria on many entries matched by name.

Project Criteria
----------------

Module :py:mod:`dirmagic.project_types`

This module contains a variety of directory criteria describing project
types.

Each :py:class:`dirmagic.core_criteria.ProjectType` provides a
name and a category for the project type along with the criterion describing
the expected directory structure.

By default :py:func:`dirmagic.identify_project` uses all project types in this
module to determine matching the project types.

Please see the :ref:`development` section for instructions on how to contribute
to this collection.

.. _pattern-criteria:

Pattern Criteria
----------------

Module :py:mod:`dirmagic.pattern_criteria`

Detect existing files by pattern and apply a criterion for each match,
based on the match filename.

Examples:

* The generic criterion ``HasFilePattern(pattern, ...)`` is equvalent to
  ``AnyMatchCriterion(pattern, HasFile(...))``

* check whether every ``*.csv`` file follows a ``day-month-year.csv``
  naming convention and the header line is ``time,transaction,balance``.

.. code-block:: python

    AllMatchCriterion(
        r"^.*?([^/]*)\.csv$",
        MatchesPattern("{0[1]}", r"\d\d-\d\d-\d\d\d\d") &
        HasFile("{0[0]}", "time,transaction,balance", n=1, fixed=True)
    )

* check whether there is a ``*.jpg`` or ``*.png`` file for each ``*.txt``
  file.

.. code-block:: python

  AllMatchCriterion(
    r"(.*)\.txt$",
    HasFile("{0[1]}.jpg") | HasFile("{0[1]}.png")
  )

* check whether there are any MacOS file properties

.. code-block:: python

    AnyMatchCriterion(
        r"(^|.*/)\.DS_Store$",
        HasFile("{0[0]}")
    )

The criteria :py:class:`dirmagic.pattern_criteria.AnyMatchCriterion` and
:py:class:`dirmagic.pattern_criteria.AllMatchCriterion` work as follows:

* All entries in the test directory will be considered (breadth first), the
  search can be narrowed down by limiting the depth or the entry types
  returned.
* The entries will be matched against the regular expression pattern using
  :external+python:py:func:`re.search` and when successful the result is
  returned.
* For each match the criterion is adjusted according to this match result by
  using the :external+python:py:meth:`str.format` function on one (or more)
  properties of the criterion (and the sub-criteria if existent).
* For each match, the adjusted criterion is tested.
* For :py:class:`dirmagic.pattern_criteria.AnyMatchCriterion`, the test is
  successful when one test is positive, for
  :py:class:`dirmagic.pattern_criteria.AllMatchCriterion` the test is
  unsuccessful when one test is negative.

The :external+python:py:meth:`re.Match.group` is used to customize the
criterion's parameters depending on the match/es:

* ``{0[0]}`` is replaced with the full match, i.e. ``match[0]``,
* ``{0[1]}``, ... is replaced with the first, ... matched group, and
* ``{0[groupname])`` is replaced with the named match, i.e.
  ``(?P<groupname>.*\.txt)``
* ``{1[groupname]}``, ... are used for nested match ciriteria, conting the
  matches from innermost (0) outwards.

The criteria :py:class:`dirmagic.pattern_criteria.MatchesPattern`,
:py:class:`dirmagic.pattern_criteria.FileMimeType`,
:py:class:`dirmagic.pattern_criteria.IsIn`, and
:py:class:`dirmagic.pattern_criteria.SuffixIsIn` are especially useful within
this context.

The criterion :py:class:`dirmagic.pattern_criteria.SpyCriterion` prints out the
parameters going into the test functions.
This helps to debug complex criteria, in addition to examining the
:py:class:`dirmagic.core_criteria.CriterionResult`. The ``SpyCriterion`` is
always true, so it can be added at any location using ``&``.

Regular Expressions and Paths
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The module :py:mod:`dirmagic.pattern_criteria` relies heavily on regular
expressions (see :external+python:py:mod:`re`). Regular expressions have a
steep learning curve at the beginning.

Some Examples:

* use ``^`` to anchor the pattern at the beginning and ``$`` at the end of
  the string.

* an elaborate and versatile example:

.. code-block:: python

    r"^(?P<path>(?P<parent>[^/]*/)*)(?P<stem>.*?)(?P<suffix>\.[^.]+)?$""

This provides several useful elements of a path, e.g. for ``a/b/c/d.txt``:

* ``0[path]`` is ``a/b/c/``
* ``0[stem]`` is ``d``
* ``0[suffix]`` is ``.txt``
* ``0[parent]`` is ``c/``

Todo: find extension, stem of file name, path before, use ``\0``.

The function :py:func:`dirmagic.pattern_criteria.translate` converts a
glob-style pattern into a regular expression, just like
:external+python:func:`fnmatch.translate`, but wraps each wildcard into a
match group.

Todo: Demonstrate Use...

Core Criteria
-------------

Module :py:mod:`dirmagic.core_criteria`

This module provides the abstract criteria and operations on those, like ``&``,
``|`` and ``~``. The test result object is defined here as well.
