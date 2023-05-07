import mimetypes
import pathlib
import re
import typing

# todo: revisit need for trying to import this
# helps with mypy and sphinx typehints
try:
    import rich
except ImportError:
    pass

from .core_criteria import Criterion, CriterionResult, PathSpec

try:
    re_pattern_type = re.Pattern[str]
    re_match_type = re.Match[str]
except TypeError:
    # python 3.7 and 3.8
    re_pattern_type = re.Pattern  # type: ignore[misc]
    re_match_type = re.Match  # type: ignore[misc]

__all__ = [
    "AnyMatchCriterion",
    "AllMatchCriterion",
    "FileMimeType",
    "MatchesPattern",
    "IsIn",
    "SuffixIsIn",
    "SpyCriterion",
]


# helper function
def iter_matching_entries(
    # breadth first iteration
    start_path: pathlib.Path,
    pattern: re_pattern_type,
    subpath: pathlib.Path = pathlib.Path(),
    maxdepth: int = -1,
) -> typing.Iterator[re_match_type]:
    """
    Search through all sub-directories inside ``start_path/sub_path``

    :param start_path: the directory to start the search at

    :param pattern: The pattern is matched with
        :external+python:py:func:`re.search` to the path relative to
        ``start_path``.

    :param subpath: a (relative) sub-path to limit the search to

    :param maxdepth: the maximal iteration depth, unlimited if negative, will
        always return immediately when 0.

    The sub-directories are searched breadth first.
    If a directory's name matches, the directory is not searched.

    .. warning::

        The function is not protected against cyclic symbolic links.
    """

    if maxdepth == 0:
        return

    other_dirs = []
    for entry in (start_path / subpath).iterdir():
        rel_entry = entry.relative_to(start_path)
        m = pattern.search(str(rel_entry))
        if m:
            yield m
        else:
            # really? Maybe I should do this independent of matches...
            if entry.is_dir() and maxdepth != 1:
                other_dirs.append(rel_entry)

    while other_dirs:
        yield from iter_matching_entries(
            start_path, pattern, other_dirs.pop(0), maxdepth - 1
        )


class MatchesPattern(Criterion):
    # only makes sense with expanded pattern
    """
    Checks whether the path is matching the pattern.

    :param name_template: name to use, expanded on test
    :param pattern: pattern to match against
    """

    def __init__(
        self, name_template: str, pattern: typing.Union[str, re_pattern_type]
    ):
        self.name_template = name_template
        self.pattern = re.compile(pattern)

    def expand_pattern(
        self,
        *args: typing.Tuple[typing.Any, ...],
        **kwargs: typing.Dict[str, typing.Any],
    ) -> Criterion:
        return MatchesPattern(
            self.name_template.format(*args, **kwargs), self.pattern
        )

    def test(
        self,
        dir: PathSpec,
        *args: typing.Tuple[typing.Any, ...],
        **kwargs: typing.Dict[str, typing.Any],
    ) -> CriterionResult:
        # nothing really done with dir?!
        if args or kwargs:
            return self.expand_pattern(*args, **kwargs).test(dir)
        return CriterionResult(
            self.pattern.search(self.name_template) is not None, self, dir
        )

    def describe(self) -> str:
        return f"`{self.name_template}` matches `{self.pattern.pattern}`"


class IsIn(Criterion):
    """
    Checks whether the name of the file is one of the listed names.

    :param name_template: name - expanded if used with pattern matching
    :param names: names expected
    """

    def __init__(self, name_template: str, names: typing.List[str]):
        self.names = list(names)
        self.name_template = str(name_template)

    def expand_pattern(
        self,
        *args: typing.Tuple[typing.Any, ...],
        **kwargs: typing.Dict[str, typing.Any],
    ) -> Criterion:
        return IsIn(
            pathlib.Path(self.name_template.format(*args, **kwargs)).name,
            self.names,
        )

    def test(
        self,
        dir: PathSpec,
        *args: typing.Tuple[typing.Any, ...],
        **kwargs: typing.Dict[str, typing.Any],
    ) -> CriterionResult:
        if args or kwargs:
            self.expand_pattern(*args, **kwargs).test(dir)
        return CriterionResult(self.name_template in self.names, self, dir)

    def describe(self) -> str:
        return f"`{self.name_template}` is in {self.names}"


class SuffixIsIn(Criterion):
    """
    Checks whether the suffix of the filename is one of the listed
    suffixes.

    :param name_template: name - expanded if used with pattern matching
    :param suffixes: suffixes expected, contains the dot (like ``.txt``)
    """

    def __init__(self, name_template: str, suffixes: typing.List[str]):
        self.name_template = str(name_template)
        self.suffixes = list(suffixes)

    def expand_pattern(
        self,
        *args: typing.Tuple[typing.Any, ...],
        **kwargs: typing.Dict[str, typing.Any],
    ) -> Criterion:
        return SuffixIsIn(
            self.name_template.format(*args, **kwargs), self.suffixes
        )

    def test(
        self,
        dir: PathSpec,
        *args: typing.Tuple[typing.Any, ...],
        **kwargs: typing.Dict[str, typing.Any],
    ) -> CriterionResult:
        if args or kwargs:
            return self.expand_pattern(*args, **kwargs).test(dir)
        return CriterionResult(
            pathlib.Path(self.name_template).suffix in self.suffixes, self, dir
        )

    def describe(self) -> str:
        return f"the suffix of `{self.name_template}` is in {self.suffixes}"


class FileMimeType(Criterion):
    """
    Use :external+python:py:func:`mimetypes.guess_type` to determine
    whether the mime type of the ``filename`` is as expected.

    :param filename: the filename used to guess the mime type
    :param mimetype: the mime type expected
    """

    def __init__(self, filename: PathSpec, mimetype: str):
        self.filename = str(filename)
        self.mimetype = str(mimetype)

    def expand_pattern(
        self, *args: typing.Any, **kwargs: typing.Any
    ) -> Criterion:
        return FileMimeType(
            self.filename.format(*args, **kwargs), self.mimetype
        )

    def test(
        self, dir: PathSpec, *args: typing.Any, **kwargs: typing.Any
    ) -> CriterionResult:
        if args or kwargs:
            return self.expand_pattern(*args, **kwargs).test(dir)

        mimetype, _ = mimetypes.guess_type(str(self.filename))
        return CriterionResult(
            mimetype is not None and mimetype == self.mimetype,
            self,
            dir,
        )

    def describe(self) -> str:
        return (
            f"the mime type of filename `{self.filename}` is `{self.mimetype}`"
        )


class SpyCriterion(Criterion):
    """
    Helps debugging criteria by printing all test arguments.
    """

    def test(
        self, dir: PathSpec, *args: typing.Any, **kwargs: typing.Any
    ) -> CriterionResult:
        """
        This test prints the test arguments to stdout and returns True.
        Link this crtierion with ``&`` to the criteria you want to debug.
        """
        print("spy output", dir, args, kwargs)
        return CriterionResult(True, self, dir)

    def describe(self) -> str:
        return "SpyCriterion: always True and prints out the test parameters"


class AnyMatchCriterion(Criterion):
    """
    Tests a criterion on entries matching. Is successful when any matching
    entry is tested successfully.

    :param pattern: regular expression pattern to match entries
    :param criterion: criterion to test on each match
    """

    def __init__(self, pattern: str, criterion: Criterion):
        self.pattern = re.compile(pattern)
        self.criterion = criterion
        super().__init__()

    def test(
        self,
        dir: PathSpec,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> CriterionResult:
        assert not (args or kwargs)
        all_res = []
        dir = pathlib.Path(dir)
        for match in iter_matching_entries(dir, self.pattern, maxdepth=-1):
            res = self.criterion.test(
                dir, match[0], *match.groups(), **match.groupdict()
            )
            all_res.append(res)
            if res:
                # early exit
                return CriterionResult(True, self, dir, tuple(all_res))

        return CriterionResult(False, self, dir, tuple(all_res))

    def rich_tree(self) -> "rich.tree.Tree":
        from rich.tree import Tree

        t = Tree(f"for at least one file matching `{self.pattern.pattern}`")
        t.add(self.criterion.rich_tree())

        return t

    def describe(self) -> str:
        return (
            f"Tests whether the criterion `{self.criterion.describe()}` is "
            f"true for at least one entry matching `{self.pattern.pattern}`"
        )


class AllMatchCriterion(Criterion):
    """
    Tests a criterion on entries matching. Is successful when all
    matching entries are tested successfully.

    :param pattern: regular expression pattern to match entries
    :param criterion: criterion to test on each match
    """

    def __init__(self, pattern: str, criterion: Criterion):
        # for now pattern only regular expressions
        self.pattern = re.compile(pattern)
        self.criterion = criterion
        super().__init__()

    def test(
        self,
        dir: PathSpec,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> CriterionResult:
        assert not (args or kwargs)
        all_res = []
        dir = pathlib.Path(dir)

        for match in iter_matching_entries(dir, self.pattern, maxdepth=-1):
            res = self.criterion.test(
                dir, match[0], *match.groups(), **match.groupdict()
            )
            all_res.append(res)
            if not res:
                # early exit
                return CriterionResult(False, self, dir, tuple(all_res))

        return CriterionResult(True, self, dir, tuple(all_res))

    def rich_tree(self) -> "rich.tree.Tree":
        from rich.tree import Tree

        t = Tree(f"for all files matching `{self.pattern.pattern}`")
        t.add(self.criterion.rich_tree())

        return t

    def describe(self) -> str:
        return (
            f"Tests whether the criterion `{self.criterion.describe()}` is "
            f"true for all entries matching `{self.pattern.pattern}`"
        )


@typing.no_type_check
def translate(pat: str) -> str:
    """Translate a shell PATTERN to a regular expression.
    There is no way to quote meta-characters.

    This is :external+python:py:func:`fnmatch.translate`, but capturing each
    matched group.
    """

    STAR = object()
    res = []
    add = res.append
    i, n = 0, len(pat)
    while i < n:
        c = pat[i]
        i = i + 1
        if c == "*":
            # compress consecutive `*` into one
            if (not res) or res[-1] is not STAR:
                add(STAR)
        elif c == "?":
            add("(.)")
        elif c == "[":
            j = i
            if j < n and pat[j] == "!":
                j = j + 1
            if j < n and pat[j] == "]":
                j = j + 1
            while j < n and pat[j] != "]":
                j = j + 1
            if j >= n:
                add("\\[")
            else:
                stuff = pat[i:j]
                if "-" not in stuff:
                    stuff = stuff.replace("\\", r"\\")
                else:
                    chunks = []
                    k = i + 2 if pat[i] == "!" else i + 1
                    while True:
                        k = pat.find("-", k, j)
                        if k < 0:
                            break
                        chunks.append(pat[i:k])
                        i = k + 1
                        k = k + 3
                    chunk = pat[i:j]
                    if chunk:
                        chunks.append(chunk)
                    else:
                        chunks[-1] += "-"
                    # Remove empty ranges -- invalid in RE.
                    for k in range(len(chunks) - 1, 0, -1):
                        if chunks[k - 1][-1] > chunks[k][0]:
                            chunks[k - 1] = chunks[k - 1][:-1] + chunks[k][1:]
                            del chunks[k]
                    # Escape backslashes and hyphens for set difference (--).
                    # Hyphens that create ranges shouldn't be escaped.
                    stuff = "-".join(
                        s.replace("\\", r"\\").replace("-", r"\-")
                        for s in chunks
                    )
                # Escape set operations (&&, ~~ and ||).
                stuff = re.sub(r"([&~|])", r"\\\1", stuff)
                i = j + 1
                if not stuff:
                    # Empty range: never match.
                    add("(?!)")
                elif stuff == "!":
                    # Negated empty range: match any character.
                    add("(.)")
                else:
                    if stuff[0] == "!":
                        stuff = "^" + stuff[1:]
                    elif stuff[0] in ("^", "["):
                        stuff = "\\" + stuff
                    add(f"([{stuff}])")
        else:
            add(re.escape(c))
    assert i == n

    # Deal with STARs.
    inp = res
    res = []
    add = res.append
    i, n = 0, len(inp)
    # Fixed pieces at the start?
    while i < n and inp[i] is not STAR:
        add(inp[i])
        i += 1
    # Now deal with STAR fixed STAR fixed ...
    # For an interior `STAR fixed` pairing, we want to do a minimal
    # .*? match followed by `fixed`, with no possibility of backtracking.
    # Atomic groups ("(?>...)") allow us to spell that directly.
    # Note: people rely on the undocumented ability to join multiple
    # translate() results together via "|" to build large regexps matching
    # "one of many" shell patterns.
    while i < n:
        assert inp[i] is STAR
        i += 1
        if i == n:
            add("(.*)")
            break
        assert inp[i] is not STAR
        fixed = []
        while i < n and inp[i] is not STAR:
            fixed.append(inp[i])
            i += 1
        fixed = "".join(fixed)
        if i == n:
            add("(.*)")
            add(fixed)
        else:
            add(f"(?>(.*?){fixed})")
    assert i == n
    res = "".join(res)
    return rf"(?s:{res})\Z"
