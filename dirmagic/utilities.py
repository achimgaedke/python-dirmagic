import os
import pathlib
import typing

from .core_criteria import PathSpec


def get_start_path(path: PathSpec = ".", resolve_path: bool = False) -> pathlib.Path:
    """
    Determines the start path for the root directory search.

    ``resolve_path`` will use pathlib.resolve_path to get an absolute start
    path. Otherwise ``os.path.abspath`` is used (default).
    """
    if resolve_path:
        abspath = pathlib.Path(path).resolve()
    else:
        abspath = pathlib.Path(os.path.abspath(path))
    if not abspath.exists():
        raise FileNotFoundError(f"`{path}` does not exist.")
    if not abspath.is_dir():
        return abspath.parent
    return abspath


def list_search_dirs(
    path: PathSpec = ".",
    limit_parents: typing.Union[int, None] = None,
    resolve_path: bool = False,
) -> typing.List[pathlib.Path]:
    """
    Determine the (parent) directories to test against the root criteria.

    ``path`` - the start path - will be converted into an asbolute path

    ``resolve_path`` will use ``pathlib.resolve_path`` to get an absolute start
    path. Otherwise ``os.path.abspath`` is used (default).

    ``limit_parents`` if None (default) all parents are considered, a
    positive number will consider the next n parents. A negative number
    will limit the search to the -limit_parents level in the file system.
    """
    start_path = get_start_path(path, resolve_path)
    # slicing pathlib.Path.parents is supportered since python-3.10 only
    return [start_path, *list(start_path.parents)[slice(limit_parents)]]
