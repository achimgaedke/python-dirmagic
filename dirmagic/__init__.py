# this file defines the toplevel namespace for dirmagic
from . import core_criteria, generic_criteria, pattern_criteria, project_types
from .functions import find_projects, find_root, identify_project

__all__ = [
    "core_criteria",
    "generic_criteria",
    "pattern_criteria",
    "project_types",
    "find_projects",
    "find_root",
    "identify_project",
]
