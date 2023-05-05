import abc
import pathlib
import typing

# todo: revisit need for trying to import this
# helps with mypy and sphinx typehints
try:
    import rich
except ImportError:
    pass

PathSpec = typing.Union[str, pathlib.Path]
"""
Path types expected by the functions in this package.
"""


class CriterionResult(typing.NamedTuple):
    """
    Returns the result of the check and the tests the result is based on.

    The truthiness of the object reflects the test result, so it can be
    used in conditions straight away:

    .. code-block::

        if is_dvc_root.test(data_repo):
            with dvc.api.open(
                'data/my_data.csv',
                repo=data_repo
            ) as f:
                # ... f is a file-like object that can be processed normally.

    The methods :py:meth:`simple_tree`, :py:meth:`rich_tree` and
    :py:meth:`reason` help to inspect the result.
    """

    result: bool
    "test result"

    criterion: "Criterion"
    "test criterion"

    path: PathSpec
    "path tested"

    sub_results: typing.Tuple["CriterionResult", ...] = ()
    "results of sub-tests to evaluate this criterion"

    def __bool__(self) -> bool:
        return self.result

    def reason(self) -> str:
        """
        The reason is a human readable text describing why the check gave
        the result as it did. If the check is successful, then the reason
        can be the same as the description. If the check fails, then the
        reason should contain a statement why it failed, i.e. the negation of
        the successful reason.
        """
        if isinstance(self.criterion, AnyCriteria):
            if self.result:
                return " or ".join(r.reason() for r in self.sub_results)
            else:
                # todo: avoid the not (not (...))
                return " and ".join(
                    f"not ({r.reason()})" for r in self.sub_results
                )

        if isinstance(self.criterion, AllCriteria):
            if self.result:
                return " and ".join(r.reason() for r in self.sub_results)
            else:
                # todo: avoid the not (not (...))
                return " or ".join(
                    f"not ({r.reason()})" for r in self.sub_results
                )

        if isinstance(self.criterion, NotCriterion):
            if self.result:
                return self.criterion.describe()
            else:
                # avoid the not (not (...))
                return self.criterion.criterion.describe()

        if self.result:
            return self.criterion.describe()
        else:
            return f"not ({self.criterion.describe()})"

    @staticmethod
    def indent_text(text: str, indent: str) -> str:
        return "".join(
            f"{indent}{line}" for line in text.splitlines(keepends=True)
        )

    def simple_tree(self) -> str:
        """
        Simple result tree with (nested) indented lines
        """
        # todo: same with rich module
        indent = " " * 4
        result_string = f"{str(self.result).upper()}: "
        if self.sub_results:
            sub_result_string = "\n".join(
                self.indent_text(r.simple_tree(), indent)
                for r in self.sub_results
            )

            if isinstance(self.criterion, AnyCriteria):
                result_string += "OR"
                if len(self.sub_results) != len(self.criterion.criteria):
                    result_string += f""" ({len(self.criterion.criteria) -
                        len(self.sub_results)} untested criteria not listed)"""
            elif isinstance(self.criterion, AllCriteria):
                result_string += "AND"
                if len(self.sub_results) != len(self.criterion.criteria):
                    result_string += f""" ({len(self.criterion.criteria) -
                        len(self.sub_results)} untested criteria not listed)"""
            elif isinstance(self.criterion, NotCriterion):
                result_string += "NOT"
            elif isinstance(self.criterion, ProjectType):
                result_string += f"`{self.criterion.name}` project type"
            else:
                # add warning for unknown?
                result_string += f"`{type(self.criterion)}` criterion"

            return f"{result_string}\n{sub_result_string}"

        return f"{result_string}{self.criterion.describe()}"

    def rich_tree(self) -> "rich.tree.Tree":
        """
        Result tree rendered with rich text layout using
        :external:py:class:`rich.tree.Tree`.

        Please install the :external+rich:ref:`rich package <Introduction>`
        (see :ref:`optional-dependencies`).
        """
        from rich.tree import Tree

        result_tree = Tree("")
        if self.result:
            result_string = ":heavy_check_mark: "
        else:
            result_string = ":cross_mark: "
        if self.sub_results:
            for r in self.sub_results:
                result_tree.add(r.rich_tree())

            if isinstance(self.criterion, AnyCriteria):
                result_string += "OR"
                if len(self.sub_results) != len(self.criterion.criteria):
                    result_string += f""" ({len(self.criterion.criteria) -
                      len(self.sub_results)} untested criteria not listed)"""
            elif isinstance(self.criterion, AllCriteria):
                result_string += "AND"
                if len(self.sub_results) != len(self.criterion.criteria):
                    result_string += f""" ({len(self.criterion.criteria) -
                      len(self.sub_results)} untested criteria not listed)"""
            elif isinstance(self.criterion, NotCriterion):
                result_string += "NOT"
            elif isinstance(self.criterion, ProjectType):
                result_string += f"`{self.criterion.name}` project type"
            else:
                result_string += f"`{type(self.criterion).__name__}` criterion"

            result_tree.label = result_string

            return result_tree

        result_tree.label = f"{result_string}{self.criterion.describe()}"
        return result_tree


class Criterion(abc.ABC):
    """
    Abstract base class of a test criterion for a directory.

    The :py:meth:`Criterion.test` method returns the result of a test.

    Criteria can be combined wiht the logical operators ``&``, ``|``, ``~``.
    """

    def describe(self) -> str:
        """
        Describes the test criterion.
        """
        return type(self).__name__

    def __repr__(self) -> str:
        return f"<{type(self).__name__}: {self.describe().capitalize()}>"

    @abc.abstractmethod
    def test(self, dir: PathSpec) -> CriterionResult:
        """
        Tests whether the criterion is met for ``path``.
        """
        ...

    def __or__(self, other: "Criterion") -> "AnyCriteria":
        """
        Support ``|`` operator for logical or.
        """
        if isinstance(other, AnyCriteria):
            return AnyCriteria(self, *other.criteria)
        return AnyCriteria(self, other)

    def __and__(self, other: "Criterion") -> "AllCriteria":
        """
        Support ``&`` operator for logical and.
        """
        if isinstance(other, AllCriteria):
            return AllCriteria(self, *other.criteria)
        return AllCriteria(self, other)

    def __invert__(self) -> "Criterion":
        """
        Support ``~`` operator for logical not/inversion.
        """
        return NotCriterion(self)

    def rich_tree(self) -> "rich.tree.Tree":
        """
        Display the criterion as a :external:py:class:`rich.tree.Tree`.

        :rtype: :external:py:class:`rich.tree.Tree`
        """
        from rich.tree import Tree

        # simple tree leaf
        return Tree(self.describe())


class AnyCriteria(Criterion):
    """
    The directory matches when at least one of the criteria is met.

    Criteria can be linked together with ``|`` to form :py:class:`AnyCriteria`.
    """

    def __init__(self, *criteria: Criterion):
        self.criteria = criteria
        super().__init__()

    def describe(self) -> str:
        return " or ".join(c.describe() for c in self.criteria)

    def test(self, dir: PathSpec) -> CriterionResult:
        results = []
        for c in self.criteria:
            r = c.test(dir)
            results.append(r)
            if r:
                return CriterionResult(True, self, dir, tuple(results))
        return CriterionResult(False, self, dir, tuple(results))

    def __or__(self, other: Criterion) -> "AnyCriteria":
        if isinstance(other, AnyCriteria):
            return AnyCriteria(*self.criteria, *other.criteria)
        return AnyCriteria(*self.criteria, other)

    def rich_tree(self) -> "rich.tree.Tree":
        from rich.tree import Tree

        t = Tree("OR")
        for c in self.criteria:
            t.add(c.rich_tree())

        return t


class AllCriteria(Criterion):
    """
    The directory matches when all criteria are met.

    Criteria can be linked together with ``&`` to form :py:class:`AllCriteria`.
    """

    def __init__(self, *criteria: Criterion):
        self.criteria = criteria
        super().__init__()

    def describe(self) -> str:
        descriptions = []
        for c in self.criteria:
            c_description = c.describe()
            if isinstance(c, AnyCriteria):
                # make sure the nested "or" clauses stay together
                c_description = f"({c_description})"
            descriptions.append(c_description)
        return " and ".join(descriptions)

    def test(self, dir: PathSpec) -> CriterionResult:
        results = []
        for c in self.criteria:
            r = c.test(dir)
            results.append(r)
            if not r:
                return CriterionResult(False, self, dir, tuple(results))
        return CriterionResult(True, self, dir, tuple(results))

    def __and__(self, other: Criterion) -> "AllCriteria":
        if isinstance(other, AllCriteria):
            return AllCriteria(*self.criteria, *other.criteria)
        return AllCriteria(*self.criteria, other)

    def rich_tree(self) -> "rich.tree.Tree":
        from rich.tree import Tree

        t = Tree("AND")
        for c in self.criteria:
            t.add(c.rich_tree())

        return t


class NotCriterion(Criterion):
    def __init__(self, criterion: Criterion):
        self.criterion = criterion
        super().__init__()

    def describe(self) -> str:
        return f"not ({self.criterion.describe()})"

    def test(self, dir: PathSpec) -> CriterionResult:
        result = self.criterion.test(dir)
        return CriterionResult(not result.result, self, dir, (result,))

    def __invert__(self) -> "Criterion":
        """
        Convert double not to original criterion.
        """
        return self.criterion

    def rich_tree(self) -> "rich.tree.Tree":
        from rich.tree import Tree

        t = Tree("NOT")
        t.add(self.criterion.rich_tree())

        return t


class CriterionFromTestFun(Criterion):
    """
    Create a criterion by providing a test function and optional description.
    """

    def __init__(
        self,
        testfun: typing.Callable[[PathSpec], bool],
        description: typing.Optional[str] = None,
    ):
        # todo: check whether testfun has one path argument
        assert callable(testfun)
        self.testfun = testfun
        if description is None:
            self.description = f"Test Function `{testfun.__name__}`"
        else:
            self.description = description
        super().__init__()

    def describe(self) -> str:
        return self.description

    def test(self, dir: PathSpec) -> CriterionResult:
        return CriterionResult(self.testfun(dir), self, dir)


class ProjectType(Criterion):
    """
    Defines a project type with a name, a category and the test criterion.
    """

    name: str
    """
    project name
    """
    category: str
    """
    categories like: version control, packaging, IDE
    """
    criterion: Criterion
    """
    The criterion to test the directory
    """

    def __init__(self, name: str, category: str, criterion: Criterion):
        self.criterion = criterion
        self.name = name
        self.category = category
        self.__doc__ = f"{self.name}, {self.category}"

    def describe(self) -> str:
        return f"{self.category}, {self.name}"

    def test(self, dir: PathSpec) -> CriterionResult:
        result = self.criterion.test(dir)
        return CriterionResult(result.result, self, dir, (result,))

    def rich_tree(self) -> "rich.tree.Tree":
        from rich.tree import Tree

        t = Tree(f"`{self.name}` project type")
        t.add(self.criterion.rich_tree())

        return t
