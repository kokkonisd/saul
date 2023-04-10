"""Definitions for the package-level information for saul."""

import importlib.resources

import saul

__version_info__ = ("0", "1", "1")
__version__ = ".".join(__version_info__)

with importlib.resources.as_file(
    importlib.resources.files(saul).joinpath("license_templates")
) as path:
    LICENSES_DIR = str(path)
