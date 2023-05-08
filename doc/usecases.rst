.. _use-cases:

Use Cases
=========

Identify Project Types
----------------------

Identify the project types contained in a directory with
:py:func:`dirmagic.identify_project`:

.. code-block:: ipython

    In [1]: from dirmagic import identify_project

    In [2]: identify_project(".")
    Out[2]: 
    [('IDE', 'Visual Studio Code project'),
     ('packaging', 'python package'),
     ('version control', 'git'),
     ('version control', 'repository')]

Find Projects
-------------

Find all directories containing a python package with
:py:func:`dirmagic.find_projects` and the python package criterion provided by
:py:mod:`dirmagic.project_types`:

.. code-block:: ipython

    In [1]: from dirmagic import find_projects, project_types

    In [2]: find_projects("/Users/achim/Code", project_types.is_python_project)
    Out[2]: 
    [PosixPath('/Users/achim/Code/python-dirmagic'),
     PosixPath('/Users/achim/Code/nbconvert'),
     PosixPath('/Users/achim/Code/py-aws-vault')]

Use Criterion Result as Boolean
-------------------------------

.. code-block:: ipython

    In [1]: from dirmagic import project_types

    In [2]: if project_types.is_git_root.test("."):
        ...:     print(open(".git/HEAD").read())
        ...: 
    ref: refs/heads/main

Find the Project Root
---------------------

Find the project root directory in the parent directories with
:py:func:`dirmagic.find_root` and a criterion from
:py:mod:`dirmagic.project_types`:

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

Commands 3 and 4 are using a default list of criteria similar to
``pyprojroot``'s default criteria.

Check Criterion Result
----------------------

Display a result of a criterion match rendered with ``rich``:

.. code-block:: ipython

    In [1]: import dirmagic

    In [2]: dirmagic.project_types.is_git_root.test(".").rich_tree()
    Out[2]: 
    ✔ `git` project type
    └── ✔ OR (1 untested criteria not listed)
        └── ✔ contains the directory `.git`


    In [3]: dirmagic.project_types.is_dvc_root.test(".").rich_tree()
    Out[3]: 
    ❌ `DVC project` project type
    └── ❌ contains the directory `.dvc`


    In [4]: print(dirmagic.project_types.is_dvc_root.test(".").simple_tree())
    FALSE: `DVC project` project type
        FALSE: contains the directory `.dvc`

The method :py:meth:`dirmagic.core_criteria.CriterionResult.simple_tree`
returns a string displaying the result tree using indentation only, no ``rich``
package required here.

Custom Criteria
---------------

Build up a custom criterion using the generic criteria classes in
:py:mod:`dirmagic.generic_criteria` and the logical operators
``|`` (or), ``&`` (and) and ``~`` (not).

.. code-block:: ipython

    In [1]: from dirmagic.generic_criteria import HasDir, HasFile, HasFileGlob

    In [2]: is_my_data_dir =  (
        ...:         HasDir("data") &
        ...:         HasFileGlob("data/*.hdf") &
        ...:         HasFile("metadata.json") &
        ...:         ~ HasFile(".ignore")
        ...:     )

    In [3]: is_my_data_dir.rich_tree()
    Out[3]: 
    AND
    ├── contains the directory `data`
    ├── has a file matching `data/*.hdf`
    ├── has a file `metadata.json`
    └── NOT
        └── has a file `.ignore`

The criterion can be used with :py:func:`dirmagic.find_projects` or
:py:func:`dirmagic.find_root`.

Display a Criterion
-------------------

Display a criterion rendered with ``rich``:

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

Pattern Criteria
----------------

This is an example of a criterion checking the contents of two directories
using :py:class:`AllMatchCriterion` based on their filenames.

It asserts that:

* ``classes.txt`` exists,
* ``images/`` contains only ``png`` and ``jpg`` files,
* ``labels/`` contains only ``txt`` files, and
* each ``txt`` file has a corresponding file in ``images/``

The pattern based criteria are documented at :ref:`pattern-criteria`.

(NB: this is not an official YOLO v? definition, but rather what I ended up
using. The confusion about image dataset directory structures is highlighting
the need for coded criteria.)

.. code-block:: ipython

    In [1]: import dirmagic

    In [2]: yolo_data = (
        ...:     dirmagic.generic_criteria.HasFile("classes.txt")
        ...:     & dirmagic.pattern_criteria.AllMatchCriterion(
        ...:         r"^images/.*$",
        ...:         dirmagic.pattern_criteria.SuffixIsIn("{0[0]}", [".png", ".jpg"]),
        ...:     )
        ...:     & dirmagic.pattern_criteria.AllMatchCriterion(
        ...:         r"^labels/(.*)\.[^\.]*$",
        ...:         dirmagic.pattern_criteria.MatchesPattern("{0[0]}", r".*\.txt$")
        ...:         & (
        ...:             dirmagic.generic_criteria.HasFile("images/{0[1]}.png")
        ...:             | dirmagic.generic_criteria.HasFile("images/{0[1]}.jpg")
        ...:         ),
        ...:     )
        ...: )

    In [3]]: yolo_data.rich_tree()
    Out[3]: 
    AND
    ├── has a file `classes.txt`
    ├── for all files matching `^images/.*$`
    │   └── the suffix of `{0[0]}` is in ['.png', '.jpg']
    └── for all files matching `^labels/(.*)\.[^\.]*$`
        └── AND
            ├── `{0[0]}` matches `.*\.txt$`
            └── OR
                ├── has a file `images/{0[1]}.png`
                └── has a file `images/{0[1]}.jpg`

    In [4]: yolo_data.test("augmented_yolo_data/").rich_tree()
    Out[4]:
    ✔ AND
    ├── ✔ has a file `classes.txt`
    ├── ✔ true for all entries matching ^images/.*$
    │   ├── ✔ the suffix of `images/ee24d90d-Neill_Forks_Hut_augmented_3.jpg` is in ['.png', '.jpg']
    │   ├── ✔ the suffix of `images/9d2727d1-Tutuwai_Hut_augmented_3.jpg` is in ['.png', '.jpg']
    │   ├── ✔ the suffix of `images/6045c6fd-Mcgregor_Bivvy_augmented_3.jpg` is in ['.png', '.jpg']
    ...
    │   └── ✔ the suffix of `images/3d20cb82-Waiorongomai_Hut_augmented_5.jpg` is in ['.png', '.jpg']
    └── ✔ true for all entries matching ^labels/(.*)\.[^\.]*$
        ├── ✔ AND
        │   ├── ✔ `labels/b55b7e80-Waitewaewae_Hut_augmented_5.txt` matches `.*\.txt$`
        │   └── ✔ OR
        │       ├── ❌ has a file `images/b55b7e80-Waitewaewae_Hut_augmented_5.png`
        │       └── ✔ has a file `images/b55b7e80-Waitewaewae_Hut_augmented_5.jpg`
        ├── ✔ AND
        │   ├── ✔ `labels/5032deda-Dorset_Ridge_Hut_augmented_5.txt` matches `.*\.txt$`
        │   └── ✔ OR
        │       ├── ❌ has a file `images/5032deda-Dorset_Ridge_Hut_augmented_5.png`
        │       └── ✔ has a file `images/5032deda-Dorset_Ridge_Hut_augmented_5.jpg`
        ├── ✔ AND
        │   ├── ✔ `labels/62a5984d-Kime_Hut_augmented_3.txt` matches `.*\.txt$`
        │   └── ✔ OR
        │       ├── ❌ has a file `images/62a5984d-Kime_Hut_augmented_3.png`
        │       └── ✔ has a file `images/62a5984d-Kime_Hut_augmented_3.jpg`
        ...
        └── ✔ AND
            ├── ✔ `labels/fbacad57-Carkeek_Hut_augmented_6.txt` matches `.*\.txt$`
            └── ✔ OR
                ├── ❌ has a file `images/fbacad57-Carkeek_Hut_augmented_6.png`
                └── ✔ has a file `images/fbacad57-Carkeek_Hut_augmented_6.jpg`
