# root criterion features under test

import pathlib

import pytest

from dirmagic.core_criteria import (
    AllCriteria,
    AnyCriteria,
    CriterionFromTestFun,
    PathSpec,
)
from dirmagic.generic_criteria import HasEntry
from dirmagic.utilities import (
    get_start_path,
    list_search_dirs,
)
from dirmagic import find_root


def test_get_start_path(tmp_path: pathlib.Path) -> None:
    (tmp_path / "a_file.txt").touch()

    assert tmp_path == get_start_path(path=tmp_path)
    assert tmp_path == get_start_path(path=tmp_path / "a_file.txt")

    with pytest.raises(FileNotFoundError):
        assert tmp_path == get_start_path(path=tmp_path / "b")

    # at least on my mac resolve returns a different result
    # todo: build up a proper fixutre with a sym link
    assert tmp_path.resolve() == get_start_path(
        path=tmp_path, resolve_path=True
    )


def test_list_search_dirs(tmp_path: pathlib.Path) -> None:
    nested_dirs = tmp_path / "a/b/c/d/e/f"
    nested_dirs.mkdir(parents=True)

    all_search_dirs = list_search_dirs(path=nested_dirs)
    assert all_search_dirs[0] == nested_dirs
    assert [d.name for d in all_search_dirs[:6]] == [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
    ][::-1]

    search_dirs = list_search_dirs(path=nested_dirs, limit_parents=2)
    assert search_dirs == all_search_dirs[:3]  # one current dir, 2 parents

    search_dirs = list_search_dirs(path=nested_dirs, limit_parents=-2)
    assert (
        search_dirs == all_search_dirs[:-2]
    )  # leave out the last two entries

    search_dirs = list_search_dirs(
        path=nested_dirs, limit_parents=-len(all_search_dirs) - 2
    )
    assert search_dirs == [nested_dirs]  # only current dir


def test_find_functions(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "my_file").touch()
    (tmp_path / "a").mkdir()

    assert HasEntry("my_file").test(tmp_path)
    assert not HasEntry("my_file.txt").test(tmp_path)

    # test that non-existing root is returned as None
    with pytest.raises(FileNotFoundError):
        find_root(tmp_path, HasEntry("my_file_not there"))

    with pytest.raises(FileNotFoundError):
        find_root(tmp_path / "b", HasEntry("my_file.txt"))


def test_any_criteria(tmp_path: pathlib.Path) -> None:
    test_dir = tmp_path
    (test_dir / "my_file").touch()
    (test_dir / "a/b/c").mkdir(parents=True)

    combined_criteria = HasEntry("b") | HasEntry("my_file")
    assert isinstance(combined_criteria, AnyCriteria)

    assert combined_criteria.test(test_dir)
    assert combined_criteria.test(test_dir / "a")
    assert not combined_criteria.test(test_dir / "b")

    assert (
        combined_criteria.describe()
        == "contains the entry `b` or contains the entry `my_file`"
    )

    combined_criteria_3 = HasEntry("c") | combined_criteria
    assert isinstance(combined_criteria_3, AnyCriteria)
    assert len(combined_criteria_3.criteria) == 3


def test_all_criteria(tmp_path: pathlib.Path) -> None:
    test_dir = tmp_path
    (test_dir / "my_file").touch()
    (test_dir / "a/b/c").mkdir(parents=True)

    combined_criteria = HasEntry("a") & HasEntry("my_file")
    assert isinstance(combined_criteria, AllCriteria)

    assert combined_criteria.test(test_dir)
    assert not (combined_criteria & HasEntry("b")).test(test_dir)

    assert (
        combined_criteria.describe()
        == "contains the entry `a` and contains the entry `my_file`"
    )
    assert find_root(
        test_dir / "a/b", combined_criteria, return_reason=True
    ) == (
        test_dir,
        "contains the entry `a` and contains the entry `my_file`",
    )

    combined_all_any = combined_criteria & HasEntry("b") | HasEntry("a")
    assert isinstance(
        combined_all_any, AnyCriteria
    )  # due to operator precedence
    assert combined_all_any.test(test_dir)

    # this time the other way round
    combined_all_any = HasEntry("a") | HasEntry("b") & combined_criteria
    assert isinstance(
        combined_all_any, AnyCriteria
    )  # due to operator precedence
    assert combined_all_any.test(test_dir)

    assert find_root(test_dir / "a", combined_all_any)
    assert find_root(test_dir / "a", combined_all_any, return_reason=True) == (
        test_dir,
        "contains the entry `a`",
    )


def test_testfun_criterion(tmp_path: pathlib.Path) -> None:
    (tmp_path / "rrrr").mkdir()
    (tmp_path / "rrrr" / "rrrr.Rproj").touch()

    def test_rproj_fun(dir: PathSpec) -> bool:
        tst_dir = pathlib.Path(dir)
        return (tst_dir / f"{tst_dir.name}.Rproj").is_file()

    fun_description = "has Rproj settings file"
    rproj_test = CriterionFromTestFun(
        testfun=test_rproj_fun, description=fun_description
    )
    assert rproj_test.describe() == fun_description

    test_result = rproj_test.test(tmp_path)
    assert not test_result
    assert test_result.reason() == f"not ({fun_description})"

    test_result = rproj_test.test(tmp_path / "rrrr")
    assert test_result
    assert test_result.reason() == fun_description

    rproj_test = CriterionFromTestFun(test_rproj_fun)
    assert rproj_test.describe() == "Test Function `test_rproj_fun`"

    with pytest.raises(AssertionError):
        CriterionFromTestFun(fun_description)  # type: ignore[arg-type]
