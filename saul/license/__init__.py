"""The license module for saul.

This module contains definitions used in the license parser & generator.
"""

import enum
from dataclasses import dataclass
from typing import Optional


@enum.unique
class LicenseInputElement(enum.Enum):
    """Enumerate all the possible data entries needed to complete a license text."""

    COPYRIGHT_HOLDERS = "copyright_holders"
    COPYRIGHT_YEAR_RANGE = "copyright_year_range"
    ORGANIZATION = "organization"
    PROJECT_NAME = "project_name"
    HOMEPAGE = "homepage"


@dataclass
class LicenseReplaceElement:
    """Describe a license replace element.

    A replace element defines a string to replace by a license input element in the
    license body.

    :ivar string: the string to replace.
    :ivar element: the element to replace the string by.
    """

    string: str
    element: LicenseInputElement


@dataclass
class License:
    """Describe a (meta-)license object.

    :ivar full_name: the full, human-readable name of the license.
    :ivar spdx_id: the SPDX ID of the license.
    :ivar body: the raw text body of the license.
    :ivar replace: a list of dictionaries dictating which strings should be replaced
        by what input elements in the raw license body.
    :ivar note: a note accompanying the license.
    """

    full_name: str
    spdx_id: str
    body: str
    replace: list[LicenseReplaceElement]
    note: Optional[str]
