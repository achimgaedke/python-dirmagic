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

Generic criteria can be combined using the operators ``&``, ``|`` and negated
with ``~``. Most generic criteria can be used within
:py:class:`dirmagic.pattern_criteria.AnyMatchCriterion` or
:py:class:`dirmagic.pattern_criteria.AllMatchCriterion` to build up complex
criteria on many entries matched by name.

.. automodule:: dirmagic.generic_criteria
    :members:
    :undoc-members:

.. _pattern-criteria:

File Pattern Criteria
---------------------

Detect existing files by pattern and apply a criterion for each match,
based on the match filename.

Examples:

* check whether every ``*.csv`` file follows a ``day-month-year.csv``
  naming convention and the header line is ``time,transaction,balance``.

.. code-block:: python

    AllMatchCriterion(
        r".*?([^/]*)\.csv$",
        MatchesPattern("{1}", r"\d\d-\d\d-\d\d\d\d") &
        HasFile("{0}", "time,transaction,balance", n=1, fixed=True)
    )

* check whether there is a ``*.jpg`` or ``*.png`` file for each ``*.txt``
  file.

.. code-block:: python

  AllMatchCriterion(
    r"(.*)\.txt$",
    HasFile("{1}.jpg") | HasFile("{1}.png")
  )

* check whether there are any MacOS file properties

.. code-block:: python

    AnyMatchCriterion(
        r"(^|.*/)\.DS_Store$",
        HasFile("{0}")
    )

The criteria :py:class:`dirmagic.pattern_criteria.AnyMatchCriterion` and
:py:class:`dirmagic.pattern_criteria.AllMatchCriterion` work as follows:

* All entries in the test directory will be considered, the search can
  be narrowed down by limiting the depth or the entry types returned.
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

The :external+python:py:meth:`re.Match.groups` and 
:external+python:py:meth:`re.Match.groupdict` data are used as input to
format the property string:

* ``{0}`` is replaced with the full match, i.e. ``match[0]``,
* ``{1}``, ... is replaced with the first, ... matched group, and
* ``groupname`` is replaced with the named match, i.e.
  ``(?P<groupname>.*\.txt)``

The criteria :py:class:`dirmagic.pattern_criteria.MatchesPattern`,
:py:class:`dirmagic.pattern_criteria.FileMimeType`,
:py:class:`dirmagic.pattern_criteria.IsIn`, and
:py:class:`dirmagic.pattern_criteria.SuffixIsIn` are especially useful within
this context.

.. automodule:: dirmagic.pattern_criteria
    :members:
    :undoc-members:

Core Criteria
-------------

The module :py:mod:`dirmagic.core_criteria` provides the abstract criteria and
operations on those, like ``&``, ``|`` and ``~``.
The test result object is defined here as well.

.. automodule:: dirmagic.core_criteria
    :members:
    :undoc-members:
