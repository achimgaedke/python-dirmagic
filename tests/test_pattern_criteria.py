import pathlib
import re

import pytest

from dirmagic.generic_criteria import HasDir, HasFile
from dirmagic.pattern_criteria import (
    AllMatchCriterion,
    AnyMatchCriterion,
    MatchesPattern,
    SpyCriterion,
    SuffixIsIn,
)


def test_match_format() -> None:
    path_name_suffix_re = (
        r"^(?P<path>(?P<parent>[^/]*/)*)(?P<stem>.*?)(?P<suffix>\.[^.]+)?$"
    )

    m = re.search(
        path_name_suffix_re,
        "a/b/c/d.txt",
    )
    assert m is not None

    assert m.groupdict() == {
        "path": "a/b/c/",
        "stem": "d",
        "suffix": ".txt",
        "parent": "c/",
    }

    assert "{0[path]}".format(m) == m["path"]
    assert "{0[0]}".format(m) == m.string
    assert "{0.string}".format(m) == "a/b/c/d.txt"

    m = re.search(
        path_name_suffix_re,
        "d.txt",
    )
    assert m is not None

    assert m.groupdict() == {
        "path": "",
        "stem": "d",
        "suffix": ".txt",
        "parent": None,
    }


@pytest.fixture
def example_fs_structure(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / "a/b/c/").mkdir(parents=True)
    (tmp_path / "my_file").write_text("a\nb\nc\nd\n")
    return tmp_path


def test_pattern_filenames(example_fs_structure: pathlib.Path) -> None:
    # assert HasFileGlob("my_*").test(example_fs_structure)
    assert AnyMatchCriterion(r"my_(.*)", HasFile(r"my_{0[1]}")).test(
        example_fs_structure
    )
    # assert HasFilePattern("_fil").test(example_fs_structure)
    assert AnyMatchCriterion(
        r"(.*)_fil(.*)", HasFile(r"{0[1]}_fil{0[2]}")
    ).test(example_fs_structure)
    # assert not HasFilePattern("^_fil").test(example_fs_structure)
    assert not AnyMatchCriterion(r"(.*[abc])", HasFile("{0[1]}")).test(
        example_fs_structure
    )
    assert AnyMatchCriterion(r"(.*[abc])", HasDir(r"{0[1]}")).test(
        example_fs_structure
    )

    # assert HasFileGlob("my_*").describe() == "has a file matching `my_*`"
    # assert (
    #     HasFilePattern("_fil").describe()
    #     == "has a file matching the regular expression `_fil`"
    # )


def test_use_cases(tmp_path: pathlib.Path) -> None:
    # only text files in directory
    # AllMatchCriterion("*", MatchPattern( ???? ))

    # make sure no file wo txt at the end
    # ~HasFile(".*[!(\.txt)]")

    (tmp_path / "a.png").touch()
    (tmp_path / "b.png").touch()
    (tmp_path / "c.jpg").touch()

    # only entries which are files with endings png, jpg, gif in dir
    assert AllMatchCriterion(
        "(.*)",
        HasFile(r"{0[1]}")
        & (
            MatchesPattern(r"{0[1]}", r".*\.png$")
            | MatchesPattern(r"{0[1]}", r".*\.jpg$")
        ),
    ).test(tmp_path)

    assert AllMatchCriterion(
        "(.*)", HasFile(r"{0[1]}") & SuffixIsIn(r"{0[1]}", [".png", ".jpg"])
    ).test(tmp_path)

    # add a .txt file
    (tmp_path / "c.txt").touch()
    assert not AllMatchCriterion(
        "(.*)",
        HasFile(r"{0[1]}")
        & (
            MatchesPattern(r"{0[1]}", r".*\.png$")
            | MatchesPattern(r"{0[1]}", r".*\.jpg$")
        ),
    ).test(tmp_path)

    assert not AllMatchCriterion(
        "(.*)", HasFile(r"{0[1]}") & SuffixIsIn(r"{0[1]}", [".png", ".jpg"])
    ).test(tmp_path)

    # just add a text file...
    assert AllMatchCriterion(
        "(.*)",
        HasFile(r"{0[1]}") & SuffixIsIn(r"{0[1]}", [".png", ".jpg", ".txt"]),
    ).test(tmp_path)
    (tmp_path / "c.txt").unlink()

    # make a deceiving directory...
    (tmp_path / "d.jpg").mkdir()
    assert not AllMatchCriterion(
        "(.*)",
        HasFile(r"{0[1]}")
        & (
            MatchesPattern(r"{0[1]}", r".*\.png$")
            | MatchesPattern(r"{0[1]}", r".*\.jpg$")
        ),
    ).test(tmp_path)


def test_file_pair_usecase(tmp_path: pathlib.Path) -> None:
    # build up a use-case like image labelling

    img_dir = tmp_path / "images"
    img_dir.mkdir()
    (img_dir / "a.png").touch()
    (img_dir / "b.jpg").touch()
    (img_dir / "c.jpg").touch()  # no labels here

    label_dir = tmp_path / "labels"
    label_dir.mkdir()
    (label_dir / "a.txt").touch()
    (label_dir / "b.txt").touch()

    (tmp_path / "classes.txt").touch()

    # hmmm, how do I make the suffix testing case insensitive?
    labeled_images_data = (
        HasFile("classes.txt")
        & AllMatchCriterion(
            "labels/.*$", HasFile(r"{0[0]}") & SuffixIsIn(r"{0[0]}", [".txt"])
        )
        & AllMatchCriterion(
            r"labels/(.*)\.txt$",
            (HasFile("images/{0[1]}.png") | HasFile("images/{0[1]}.jpg")),
            # MatchesPattern would not test for file existence.
            # Maybe first candidate for nested loop?
        )
    )
    assert labeled_images_data.test(tmp_path)

    (label_dir / "d.txt").touch()
    assert not labeled_images_data.test(tmp_path)

    (img_dir / "d.jpg").touch()
    assert labeled_images_data.test(tmp_path)


def test_nested_loops(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # nested loops

    img_dir = tmp_path / "d1"
    img_dir.mkdir()
    (img_dir / "a.png").touch()
    (img_dir / "b.png").touch()

    img_dir = tmp_path / "d2"
    img_dir.mkdir()
    (img_dir / "c.jpg").touch()
    (img_dir / "d.jpg").touch()

    t = AllMatchCriterion(
        r"^.*\..*$", AllMatchCriterion(r"^.*\..*$", SpyCriterion())
    ).test(tmp_path)
    assert t
    assert len(capsys.readouterr().out.splitlines()) == 16
