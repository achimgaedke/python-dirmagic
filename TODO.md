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

Combination of properties:

AND/OR, XOR (exactly one of...)

Usecases:

* detect project structure (just basic validation)
* verify project structure (just basic validation)
* find projects of a certain kind
* find project root

Extend:

* work on archives, repository URLs, S3, other FS... (maybe using fsspec?)

Make consumable for others:

* create package
* create documentation

* publish pip / conda
* publish documentation
