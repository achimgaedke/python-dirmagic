# TODOs

* Increase test coverage (again)
* Reduce code duplication in tree views (criterion and result)

## Pattern Match Criteria

AnyMatchCriterion / AllMatchCriterion:

* add parameters like maxdepth and subdir to *MatchCriterion
* limit search results to files or dirs only in a subdir...
* explain search depth/order
* no nested *MatchCriteria at this stage, but later
* make more obvious which criteria are useful with the match criteria.

Regular expressions and path names:

* search vs match
* explain how to limit file or dir names with regular expressions
* mention the translate function & examples

## Add criteria

* file size based, e.g. empty, min size...
* an optional libmagic criterion `magic.from_file(filename, mime=True)`

## Criterion Definitons

Explore notation like:

```python
{
    "a/b.xml": not_empty,
    "src/*.c": is_c_code,
}
```

## Extend file interface

* work on archives, repository URLs, S3, other FS... (maybe using fsspec?)

## Pipeline and packaging

* build python packages (whl, ...),
* upload package to pypi
* setup a conda project

and all this also with github supported CI pipelines.
