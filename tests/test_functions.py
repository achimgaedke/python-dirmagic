import pathlib

import pytest
from dirmagic.generic_criteria import HasEntry
from dirmagic import find_root, identify_project, find_projects
from dirmagic.project_types import is_vcs_root


def test_identify_project_function(tmp_path: pathlib.Path) -> None:
    (tmp_path / "my_file").touch()
    (tmp_path / "a").mkdir()
    assert identify_project(tmp_path) == []

    (tmp_path / ".git").mkdir()
    assert identify_project(tmp_path) == [
        ("version control", "git"),
        ("version control", "repository"),
    ]


def test_find_projects(tmp_path: pathlib.Path) -> None:
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / ".git").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "b" / "c").mkdir()
    (tmp_path / "b" / "c" / ".git").mkdir()
    (tmp_path / "not_dir").touch()

    assert find_projects(tmp_path, is_vcs_root, maxdepth=-1) == [
        tmp_path / "a",
        tmp_path / "b" / "c",
    ]

    assert find_projects(tmp_path, is_vcs_root, maxdepth=1) == [tmp_path / "a"]
    assert find_projects(tmp_path, is_vcs_root, maxdepth=0) == []


def test_find_root_function(tmp_path: pathlib.Path) -> None:
    (tmp_path / "my_file").touch()
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / ".git").mkdir()
    (tmp_path / "a" / "b").mkdir()

    # the default criterion should find a git repositories
    assert find_root(tmp_path / "a") == tmp_path / "a"
    assert find_root(tmp_path / "a" / "b") == tmp_path / "a"

    assert (
        find_root(tmp_path / "a", [HasEntry("my_file.txt"), is_vcs_root])
        == tmp_path / "a"
    )

    assert HasEntry("my_file").test(tmp_path)
    assert not HasEntry("my_file.txt").test(tmp_path)

    # test that non-existing root is returned as None
    with pytest.raises(FileNotFoundError):
        find_root(tmp_path, HasEntry("my_file_not there"))

    with pytest.raises(FileNotFoundError):
        find_root(tmp_path / "b", HasEntry("my_file.txt"))
