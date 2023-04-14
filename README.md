# dirmagic

Mission:

Just like filemagic, tells you what type of project/directory structure you're dealing with.

More in the [documetation](doc/index.rst)

## Can't wait, get started?

```bash
pip install git+https://github.com/achimgaedke/dirmagic.git
```

Simple examples:

Find all directories containing a python package:

```python
import dirmagic import find_projects, project_types

find_projects(
    "/home/achim/Code",
     project_types.python_package
)
```

Find the DVC root in your parent directories:

```python
from dirmagic import find_root, project_types

find_root(".", project_types.dvc_repository)
```

Identify project type contained in directory:

```python
from dirmagic import identify_project

identify_project("Code/some_repo")
```

See [usecases](doc/usecases.rst) for more...
