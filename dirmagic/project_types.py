from .core_criteria import ProjectType
from .generic_criteria import (
    HasBasename,
    HasDir,
    HasFile,
    HasFilePattern,
)


# https://github.com/iterative/dvc/blob/8edaef010322645ccfc83936e5b7f706ad9773a4/dvc/repo/__init__.py#L399
is_dvc_root = ProjectType("DVC project", "data pipelines", HasDir(".dvc"))
"""
`Data Version Control <https://dvc.org/>`_ (DVC) project directory
"""

is_vscode_project = ProjectType(
    "Visual Studio Code project", "IDE", HasFile(".vscode/settings.json")
)
"""
`Visual Studio Code <https://code.visualstudio.com/>`_ IDE directory

This criterion tests specifically for ``.vscode/settings.json`` as there is a
`.vscode` directory in the user's home directory.
"""

is_idea_project = ProjectType("IntelliJ IDEA project", "IDE", HasDir(".idea"))
"""
`IntelliJ IDEA <https://www.jetbrains.com/idea/>`_ project directory
"""

is_spyder_project = ProjectType("Spyder project", "IDE", HasDir(".spyproject"))
"""
`Spyder <https://docs.spyder-ide.org/>`_ IDE project directory
"""

is_anaconda_project = ProjectType(
    "Anaconda project", "IDE", HasFile("anaconda-project.yml")
)
"""
`Anaconda <https://anaconda-project.readthedocs.io/en/latest/index.html>`_ IDE project directory
"""

is_python_project = ProjectType(
    "python package",
    "packaging",
    HasFile("setup.py") | HasFile("setup.cfg") | HasFile("pyproject.toml"),
)
"""
`Python package <https://packaging.python.org/en/latest/>`_ project
"""

is_conda_feedstock = ProjectType(
    "conda feedstock",
    "packaging",
    HasFile("recipes/meta.yaml") & HasFile("conda-forge.yml"),
)
"""
`Conda Package Feedstock <https://conda-forge.org/docs/index.html>`_ project
"""

# https://github.com/r-lib/rprojroot/blob/main/R/root.R#L309
is_rstudio_project = ProjectType(
    "RStudio/Posit", "IDE", HasFilePattern("[.]Rproj$", contents="^Version: ", n=1)
)
"""
`RStudio <https://posit.co/download/rstudio-desktop/>`_ project directory
"""

is_r_package = ProjectType(
    "R package", "packaging", HasFile("DESCRIPTION", contents="^Package: ")
)
"""
`R source package <https://r-pkgs.org/structure.html#sec-source-package>`_ directory
"""

is_remake_project = ProjectType("remake", "data pipelines", HasFile("remake.yml"))
"""
`remake <https://github.com/richfitz/remake>`_ project directory
"""

is_drake_project = ProjectType("drake", "data pipelines", HasDir(".drake"))
"""
`drake <https://docs.ropensci.org/drake/>`_ project directory

drake is superceded by ``targets``, see below.
"""

# https://docs.ropensci.org/targets/reference/tar_script.html
is_targets_project = ProjectType("targets", "data pipelines", HasFile("_targets.R"))
"""
`targets <https://docs.ropensci.org/targets/index.html>`_ project directory
"""

is_pkgdown_project = ProjectType(
    "pkgdown",
    "misc",
    HasFile("_pkgdown.yml")
    | HasFile("_pkgdown.yaml")
    | HasFile("pkgdown/_pkgdown.yml")
    | HasFile("inst/_pkgdown.yml"),
)
"""
`pkgdown <https://pkgdown.r-lib.org/>`_ project directory
"""

is_projectile_project = ProjectType("projectile project", "IDE", HasFile(".projectile"))
"""
`Projectile <https://docs.projectile.mx/>`_ project directory
"""


# TODO: use subdir
# is_testthat = has_basename("testthat", c("tests/testthat", "testthat"))
# or try... but doesn't reeturn the subdir...
# is_testthat = has_dir("tests/testthat") | has_dir("testthat") | has_basename("testthat")
is_testthat = ProjectType("testthat project", "misc", HasBasename("testthat"))
"""
`testthat <https://testthat.r-lib.org/>`_ directory
"""

# Version control

is_git_root = ProjectType(
    "git", "version control", HasDir(".git") | HasFile(".git", contents="^gitdir: ")
)
"""
`git <https://git-scm.com/>`_ repository directory
"""

is_svn_root = ProjectType("subversion", "version control", HasDir(".svn"))
"""
`SVN <https://subversion.apache.org/>`_ repository directory
"""

# todo add mercurial https://www.mercurial-scm.org/ criterion

is_vcs_root = ProjectType("repository", "version control", is_git_root | is_svn_root)
"""
Any repository (git, svn, ...) directory
"""


__all__ = [
    criterion_name
    for criterion_name, project_type in globals().items()
    if isinstance(project_type, ProjectType)
]
