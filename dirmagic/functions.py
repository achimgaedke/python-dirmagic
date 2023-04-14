import pathlib
import typing

from .core_criteria import CriterionResult, PathSpec, Criterion, ProjectType
from . import project_types
from .generic_criteria import as_root_criterion, HasDir, HasEntryGlob, HasFile
from .utilities import list_search_dirs, get_start_path


def find_projects(
    path: PathSpec, criterion: typing.Any, maxdepth: int = 1
) -> typing.List[pathlib.Path]:
    """
    Search through all sub-directories inside ``path`` returning the
    directories matching the criterion.

    The sub-directories are searched breadth first.
    Once a directory is matched, it is not searched for sub-projects.

    ``maxdepth``: the maximal iteration depth, unlimited if negative, will
    always return [] when 0. Warning: The function is not protected against
    cyclic symbolic links.
    """
    if maxdepth == 0:
        return []

    the_criterion = as_root_criterion(criterion)
    start_path = get_start_path(path)

    dirs_found = []
    other_dirs = []
    for dir in start_path.iterdir():
        if not dir.is_dir():
            continue
        if the_criterion.test(dir):
            dirs_found.append(dir)
        else:
            other_dirs.append(dir)

    if maxdepth != 1:
        for dir in other_dirs:
            dirs_found.extend(find_projects(dir, criterion, maxdepth - 1))

    return dirs_found


def find_root(
    path: PathSpec = ".",
    criterion: typing.Any = None,
    return_reason: bool = False,
    **kwargs: typing.Any,
) -> typing.Union[pathlib.Path, typing.Tuple[pathlib.Path, str]]:
    """
    Find the project's root.

    ``path`` - the start path - will be converted into an asbolute path

    ``criterion``: can be a specific criterion, one of the project types or
    None (default) for a collection of criteria as used in pyprojroot.

    ``return_reason`` - if True: returns (root, result), otherwise returns root.
    In order to investigate the reason, use the ``reason()`` or the ``result_tree``
    function on the CriterionResult object.

    ``resolve_path`` will use ``pathlib.resolve_path`` to get an absolute start
    path. Otherwise ``os.path.abspath`` is used (default).

    ``limit_parents`` if None (default) all parents are considered, a
    positive number will consider the next n parents. A negative number
    will limit the search to the -limit_parents level in the file system.

    ``list_parents("/home/me/projects/fancy-project/src", limit_parents=-2)``

    will search only ``src``, ``fancy-project``, and ``projects``. A value
    of 1 will search ``src`` and ``fancy-projects``.

    Raises FileNotFoundError if no criteria were met.
    """
    parents = list_search_dirs(path, **kwargs)

    if criterion is None:
        the_criteria = [
            # use a reasonable default
            # from https://github.com/chendaniely/pyprojroot/blob/main/src/pyprojroot/here.py#L17
            HasFile(".here"),
            HasDir(".git"),
            HasEntryGlob("*.Rproj"),
            HasFile("requirements.txt"),
            HasFile("setup.py"),
            HasDir(".dvc"),
            HasDir(".spyproject"),
            HasFile("pyproject.toml"),
            HasDir(".idea"),
            HasDir(".vscode"),
        ]
    elif isinstance(criterion, (list, tuple)):
        the_criteria = [as_root_criterion(c) for c in criterion]
    else:
        the_criteria = [as_root_criterion(criterion)]

    for dir in parents:
        for the_criterion in the_criteria:
            result = the_criterion.test(dir)
            if result:
                if return_reason:
                    return dir, result.reason()
                return dir

    raise FileNotFoundError(
        f"No root directory found in {parents[0]} or its parent directories."
    )


def identify_project(
    path: PathSpec = ".",
    types_to_test: typing.Optional[typing.Sequence[ProjectType]] = None,
) -> typing.List[typing.Tuple[str, str]]:
    """
    Determines which criteria matche on path.

    Returns list of (project category, project name).
    """
    dir = get_start_path(path)
    if types_to_test is None:
        types_to_test = [
            project_type
            for project_type in project_types.__dict__.values()
            if isinstance(project_type, ProjectType)
        ]

    types_matched = []
    for project_type in types_to_test:
        result = project_type.test(dir)
        if result:
            types_matched.append(result)

    return sorted(
        (type_matched.criterion.category, type_matched.criterion.name)
        for type_matched in types_matched
        if isinstance(type_matched.criterion, ProjectType)
    )
