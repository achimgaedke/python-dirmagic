import pathlib

import pytest

from dirmagic.generic_criteria import (
    HasBasename,
    HasDir,
    HasEntry,
    HasFile,
    HasFileGlob,
    HasFilePattern,
)
from dirmagic import find_root


@pytest.fixture
def example_fs_structure(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / "a/b/c/").mkdir(parents=True)
    (tmp_path / "my_file").write_text("a\nb\nc\nd\n")
    return tmp_path


def test_has_file_criterion(example_fs_structure: pathlib.Path) -> None:
    assert list(
        HasFile.read_lines_from_file(example_fs_structure / "my_file")
    ) == [
        "a",
        "b",
        "c",
        "d",
    ]

    # test "fixed" content
    assert HasFile("my_file", "c", fixed=True).test(example_fs_structure)
    assert HasFile("my_file", "c", n=-3, fixed=True).test(example_fs_structure)
    assert HasFile("my_file", "c", n=3, fixed=True).test(example_fs_structure)
    assert not HasFile("my_file", "a", fixed=True, n=0).test(
        example_fs_structure
    )
    assert not HasFile("my_file", "", fixed=True).test(example_fs_structure)

    # test regexp matching
    assert HasFile("my_file", "[bc]").test(example_fs_structure)
    assert not HasFile("my_file", "[bc]", n=1).test(example_fs_structure)

    assert not HasFile("my_file.txt", "[bc]", n=1).test(example_fs_structure)

    # test direct use as root criterion
    assert example_fs_structure == find_root(
        example_fs_structure / "a/b/c/", HasFile("my_file")
    )

    # look at the reason
    with pytest.raises(FileNotFoundError):
        find_root(
            example_fs_structure,
            HasFile("my_file_not there"),
            return_reason=True,
        )

    assert find_root(
        example_fs_structure, HasFile("my_file"), return_reason=True
    ) == (
        pathlib.Path(example_fs_structure),
        "has a file `my_file`",
    )
    assert find_root(
        example_fs_structure,
        HasFile("my_file", "a", 1, fixed=True),
        return_reason=True,
    ) == (
        pathlib.Path(example_fs_structure),
        "has a file `my_file` and "
        "file contains a line with the contents `a` in the first 1 line/s",
    )

    assert find_root(
        example_fs_structure,
        HasFile("my_file", "[ac]", 1, fixed=False),
        return_reason=True,
    ) == (
        pathlib.Path(example_fs_structure),
        "has a file `my_file` and file contains a line matching "
        "the regular expression `[ac]` in the first 1 line/s",
    )

    # test the describe method
    assert (
        HasFile("my_file", "a", 1, fixed=True).describe()
        == "has a file `my_file` and file contains a line "
        "with the contents `a` in the first 1 line/s"
    )
    assert (
        HasFile("my_file", "[ab]", 3).describe()
        == "has a file `my_file` and file contains a line "
        "matching the regular expression `[ab]` in the first 3 line/s"
    )


def test_has_dir(example_fs_structure: pathlib.Path) -> None:
    assert HasDir("a").test(example_fs_structure)
    assert not HasDir("a").test(example_fs_structure / "b")

    assert (
        HasDir("a").test(example_fs_structure).reason()
        == "contains the directory `a`"
    )
    assert (
        HasDir("b").test(example_fs_structure).reason()
        == "not (contains the directory `b`)"
    )


def test_has_entry(example_fs_structure: pathlib.Path) -> None:
    assert HasEntry("a").test(example_fs_structure)
    assert HasEntry("a/").test(example_fs_structure)
    assert HasEntry(".").test(example_fs_structure)  # that's an odd case?!
    assert HasEntry("my_file").test(example_fs_structure)
    assert HasEntry("my_file/").test(
        example_fs_structure
    )  # oddly this succeeds, though it is a file
    assert HasEntry("my_file/.").test(
        example_fs_structure
    )  # oddly this succeeds, though it is a file
    assert not HasEntry("b").test(example_fs_structure)
    assert (
        HasEntry("a").test(example_fs_structure).reason()
        == "contains the entry `a`"
    )


def test_has_basename(example_fs_structure: pathlib.Path) -> None:
    assert HasBasename("a").test(example_fs_structure / "a")
    assert not HasBasename("a").test(example_fs_structure)
    assert HasBasename(example_fs_structure.name).test(example_fs_structure)


def test_pattern_filenames(example_fs_structure: pathlib.Path) -> None:
    assert HasFileGlob("my_*").test(example_fs_structure)
    assert HasFilePattern("_fil").test(example_fs_structure)
    assert not HasFilePattern("^_fil").test(example_fs_structure)
    assert not HasFilePattern("[ab]").test(example_fs_structure)

    assert HasFileGlob("my_*").describe() == "has a file matching `my_*`"
    assert (
        HasFilePattern("_fil").describe()
        == "has a file matching the regular expression `_fil`"
    )
