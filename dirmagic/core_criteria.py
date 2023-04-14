import abc
import pathlib
import typing

PathSpec = typing.Union[str, pathlib.Path]
"""
Path types expected by the functions in this package.
"""


class CriterionResult(typing.NamedTuple):
    """
    Returns the result of the check and the tests the result is based on.

    This allows understanding the result.
    """

    result: bool
    criterion: "Criterion"
    path: PathSpec
    sub_results: typing.Tuple["CriterionResult", ...] = ()

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
                return " and ".join(f"not ({r.reason()})" for r in self.sub_results)

        if isinstance(self.criterion, AllCriteria):
            if self.result:
                return " and ".join(r.reason() for r in self.sub_results)
            else:
                # todo: avoid the not (not (...))
                return " or ".join(f"not ({r.reason()})" for r in self.sub_results)

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
        return "".join(f"{indent}{line}" for line in text.splitlines(keepends=True))

    def result_tree(self) -> str:
        """
        Simple result tree with (nested) indented lines
        """
        # todo: same with rich module
        indent = " " * 4
        result_string = f"{str(self.result).upper()}: "
        if self.sub_results:
            sub_result_string = "\n".join(
                self.indent_text(r.result_tree(), indent) for r in self.sub_results
            )

            if isinstance(self.criterion, AnyCriteria):
                result_string += "OR"
                if len(self.sub_results) != len(self.criterion.criteria):
                    result_string += f" ({len(self.criterion.criteria) - len(self.sub_results)} untested criteria not listed)"
            elif isinstance(self.criterion, AllCriteria):
                result_string += "AND"
                if len(self.sub_results) != len(self.criterion.criteria):
                    result_string += f" ({len(self.criterion.criteria) - len(self.sub_results)} untested criteria not listed)"
            elif isinstance(self.criterion, NotCriterion):
                result_string += "NOT"
            elif isinstance(self.criterion, ProjectType):
                result_string += f"`{self.criterion.name}` project type"
            else:
                # add warning for unknown?
                result_string += f"`{type(self.criterion)}` criterion"

            return f"{result_string}\n{sub_result_string}"

        return f"{result_string}{self.criterion.describe()}"


class Criterion(abc.ABC):
    """
    Abstract base class of a test criterion for a directory.

    The ``test`` method returns the result of a test.

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

    def __invert__(self):
        """
        Support ``~`` operator for logical not/inversion.
        """
        return NotCriterion(self)


class AnyCriteria(Criterion):
    """
    The directory matches when at least one of the criteria is met.

    Criteria can be linked together with ``|`` to form ``AnyCriteria``.
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


class AllCriteria(Criterion):
    """
    The directory matches when all criteria are met.

    Criteria can be linked together with ``&`` to form ``AllCriteria``.
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


class NotCriterion(Criterion):
    def __init__(self, criterion: Criterion):
        self.criterion = criterion
        super().__init__()

    def describe(self) -> str:
        return f"not ({self.criterion.describe()})"

    def test(self, dir: PathSpec) -> CriterionResult:
        result = self.criterion.test(dir)
        return CriterionResult(not result.result, self, dir, (result,))

    def __invert__(self):
        """
        Convert double not to original criterion.
        """
        return self.criterion


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
