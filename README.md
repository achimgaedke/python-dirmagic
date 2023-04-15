# python-dirmagic

*Mission:*

`dirmagic` tells you what type of project/directory structure you're dealing with.

... just like `file`/`libmagic` for files.

Read more in the [documetation](https://python-dirmagic.readthedocs.io)

## Build Status

[![Documentation Status](https://readthedocs.org/projects/python-dirmagic/badge/?version=latest)](https://python-dirmagic.readthedocs.io/en/latest/?badge=latest)

## Can't wait, get started?

Install:

```bash
pip install git+https://github.com/achimgaedke/python-dirmagic.git
```

Simple examples:

Find all directories containing a python package:

```python
import dirmagic import find_projects, project_types

find_projects(
    "/home/achim/Code",
     project_types.is_python_project
)
```

Find the DVC root in your parent directories:

```python
from dirmagic import find_root, project_types

find_root(".", project_types.dvc_repository)
```

Identify project types contained in directory:

```python
from dirmagic import identify_project

identify_project("Code/some_repo")
```

See [Use Cases](https://python-dirmagic.readthedocs.io/en/latest/usecases.html) for more...
