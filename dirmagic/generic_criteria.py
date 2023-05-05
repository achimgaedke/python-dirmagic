import itertools
import pathlib
import re
import typing

from .core_criteria import (
    AnyCriteria,
    CriterionFromTestFun,
    PathSpec,
    Criterion,
    CriterionResult,
)


class HasFile(Criterion):
    """
    Matches if the named file is present, optionally the file's contents
    can be matched.

    :param filename: name of the file (can be in a subdirectory, ``a/b.txt``)
    :param contents: is the matching string or regular expression
    :param n: limits the number of lines searched, -1 is unlimited.
    :param fixed: if set to true, the ``contents`` is matched as string

    * if ``fixed`` is True, contents must match an entire line (wo the newline
      character).
    * if ``fixed`` is False if the contents is a regular expression matching a
      part of the line using :external+python:py:func:`re.search` (i.e. use the
      anchors ``^``, ``$`` for start and end).

    This is the reimplementation of ``has_file`` from ``rprojroot``.
    """

    def __init__(
        self,
        filename: PathSpec,
        contents: typing.Optional[str] = None,
        n: int = -1,
        fixed: bool = False,
    ):
        self.filename = filename
        self.contents = contents
        self.fixed = bool(fixed)
        self.max_lines_to_search = int(n)
        super().__init__()

    @staticmethod
    def read_lines_from_file(file: PathSpec) -> typing.Iterator[str]:
        """
        Read the lines from the text file and retruns them without the
        newline character at the end.
        """
        with open(file, "rt") as txt_file:
            yield from (line.rstrip("\n") for line in txt_file)

    def check_file_contents(self, file: PathSpec) -> bool:
        """
        Check whether in the contents of the file meets the line match
        criterion.
        """
        # early returns have the side effect that the read permission for the
        # file is not checked.
        if self.contents is None:
            return True
        if self.max_lines_to_search == 0:
            return False

        line_iterator = self.read_lines_from_file(file)

        if self.max_lines_to_search >= 0:
            line_iterator = itertools.islice(
                line_iterator,
                self.max_lines_to_search,
            )

        if self.fixed:
            fixed_pattern = self.contents

            def match_function(line: str) -> bool:
                return fixed_pattern == line

        else:
            regexp_pattern = re.compile(self.contents)

            def match_function(line: str) -> bool:
                return regexp_pattern.search(line) is not None

        return any((match_function(line) for line in line_iterator))

    def describe_contents_matching(self) -> str:
        if self.contents is None:
            return ""

        description = "file contains "

        if self.fixed:
            description += f"a line with the contents `{self.contents}`"
        else:
            description += (
                f"a line matching the regular expression `{self.contents}`"
            )

        if self.max_lines_to_search >= 0:
            description += f" in the first {self.max_lines_to_search} line/s"

        return description

    def test(self, dir: PathSpec) -> CriterionResult:
        full_filename = pathlib.Path(dir) / self.filename
        return CriterionResult(
            full_filename.is_file()
            and self.check_file_contents(full_filename),
            self,
            dir,
        )

    def describe(self) -> str:
        pattern_description = f"has a file `{self.filename}`"
        if self.contents is not None:
            pattern_description += f" and {self.describe_contents_matching()}"
        return pattern_description


class HasFilePattern(HasFile):
    """
    Check whether a file exists with a name matching regular expression pattern
    and (optionally) with matching contents.

    :param pattern: is the regular expression pattern any full path name will
        be matched against using :external+python:py:func:`re.search`. It
        searches only for entries inside the directory tested.

    See :py:class:`HasFile` for the parameters matching the contents.

    This is the reimplementation of ``has_file_pattern`` from ``rprojroot``
    (see `rprojroot reference
    <https://rprojroot.r-lib.org/reference/root_criterion.html>`_).
    """

    def __init__(
        self,
        pattern: str,
        contents: typing.Optional[str] = None,
        n: int = -1,
        fixed: bool = False,
    ):
        self.contents = contents
        self.fixed = bool(fixed)
        self.max_lines_to_search = int(n)
        super().__init__(pattern)

    def test(self, dir: PathSpec) -> CriterionResult:
        pattern = re.compile(str(self.filename))
        for full_filename in pathlib.Path(dir).iterdir():
            if (
                full_filename.is_file()
                and pattern.search(full_filename.name)
                and self.check_file_contents(full_filename)
            ):
                # todo: how to communicate the matching filename?
                return CriterionResult(True, self, dir)
        return CriterionResult(False, self, dir)

    def describe(self) -> str:
        pattern_description = (
            f"has a file matching the regular expression `{self.filename}`"
        )
        if self.contents is not None:
            pattern_description += f" and {self.describe_contents_matching()}"
        return pattern_description


class HasFileGlob(HasFile):
    """
    Check whether a file exists with a name matching the glob pattern
    and (optionally) with matching contents.

    :param pattern: Is the pattern any file path will be matched against by
        using :external+python:py:meth:`pathlib.Path.glob`. The glob pattern
        allows searching in subdirectories.

    This is a reimplementation of ``matches_glob`` of ``pyprojroot``
    (see `pyprojroot code
    <https://github.com/chendaniely/pyprojroot/blob/329e2cd6ed9f357aaa9e2785d1d7990a7a6b1100/src/pyprojroot/criterion.py#L76>`_)

    See :py:class:`HasFile` for the parameters matching the contents.
    """

    def __init__(
        self,
        pattern: str,
        contents: typing.Optional[str] = None,
        n: int = -1,
        fixed: bool = False,
    ):
        self.contents = contents
        self.fixed = bool(fixed)
        self.max_lines_to_search = int(n)
        super().__init__(pattern)

    def test(self, dir: PathSpec) -> CriterionResult:
        for full_filename in pathlib.Path(dir).glob(str(self.filename)):
            if full_filename.is_file() and self.check_file_contents(
                full_filename
            ):
                # todo: how to communicate the matching filename?
                return CriterionResult(True, self, dir)
        return CriterionResult(False, self, dir)

    def describe(self) -> str:
        pattern_description = f"has a file matching `{self.filename}`"
        if self.contents is not None:
            pattern_description += f" and {self.describe_contents_matching()}"
        return pattern_description


class HasDir(Criterion):
    """
    Match if a directory of the given name is present.
    """

    def __init__(self, dirname: PathSpec):
        self.dirname = dirname
        super().__init__()

    def test(self, dir: PathSpec) -> CriterionResult:
        return CriterionResult(
            (pathlib.Path(dir) / self.dirname).is_dir(), self, dir
        )

    def describe(self) -> str:
        return f"contains the directory `{self.dirname}`"


class HasEntry(Criterion):
    """
    Match if a filesystem entry (file/directory/link/...) of this name exists.

    Note:

    ``/`` or ``/.`` at the end of the entryname are stripped off, i.e. oddly
    ``myfile/`` will match a file - this is a sideffect of python's
    ``pathlib.Path.joinpath``. Consider using ``HasDir`` instead.
    """

    def __init__(self, entryname: PathSpec):
        self.entryname = entryname
        super().__init__()

    def test(self, dir: PathSpec) -> CriterionResult:
        return CriterionResult(
            (pathlib.Path(dir) / self.entryname).exists(), self, dir
        )

    def describe(self) -> str:
        return f"contains the entry `{self.entryname}`"


class HasEntryGlob(Criterion):
    """
    Search for filesystem entry matching the glob pattern.

    The glob pattern allows searching in subdirectories.
    """

    def __init__(
        self,
        pattern: str,
    ):
        self.pattern = pattern
        super().__init__()

    def test(self, dir: PathSpec) -> CriterionResult:
        for _ in pathlib.Path(dir).glob(self.pattern):
            # TODO return the entry found
            return CriterionResult(True, self, dir)
        return CriterionResult(False, self, dir)

    def describe(self) -> str:
        return f"has a file matching `{self.pattern}`"


Exists = HasEntry


class HasBasename(Criterion):
    """
    The directory's basename is equal to the name specified.

    :param basename: expected basename
    """

    def __init__(self, basename: str):
        self.basename = basename
        super().__init__()

    def test(self, dir: PathSpec) -> CriterionResult:
        return CriterionResult(
            self.basename == pathlib.Path(dir).name, self, dir
        )


    def describe(self) -> str:
        return f"has the basename `{self.basename}`"


def as_root_criterion(criterion: typing.Any) -> "Criterion":
    """
    Converts its input into a Criterion.
    """
    # take anything and try to make a criterion out of it
    if isinstance(criterion, Criterion):
        return criterion
    if isinstance(criterion, (str, pathlib.Path)):
        return HasFile(criterion)
    if callable(criterion):
        return CriterionFromTestFun(criterion)
    if isinstance(criterion, dict):
        return AnyCriteria(*map(as_root_criterion, criterion.values()))
    if isinstance(criterion, (list, tuple)):
        return AnyCriteria(*map(as_root_criterion, criterion))
    raise ValueError(f"cannot convert {type(criterion)} to criterion")
