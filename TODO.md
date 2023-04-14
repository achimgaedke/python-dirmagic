# TODOs

first brain dump before using an issue tracker

Describe/Incept:

* Pattern matching DSL

Subdirectory properties

* locating / matching entries
* testing properties of entries
* if there are multiple entries, define whether any or all tests must succeed

Explore notation like:

```python
{
    "a/b.xml": not_empty,
    "src/*.c": is_c_code,
}
```

Extend:

* work on archives, repository URLs, S3, other FS... (maybe using fsspec?)

Pipeline and packaging:

* build python packages (whl, ...),
* upload package to pypi
* setup a conda project

and all this also with github supported CI pipelines.
