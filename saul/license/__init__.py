"""The license module for saul.

This module contains definitions used in the license parser & generator.
"""

import enum
from dataclasses import dataclass
from typing import Optional


@enum.unique
class LicenseInputElement(enum.Enum):
    """Enumerate all the possible data entries needed to complete a license text."""

    YEAR_RANGE = "YEAR_RANGE"
    COPYRIGHT_HOLDERS = "COPYRIGHT_HOLDERS"
    ORGANIZATION = "ORGANIZATION"
    PROJECT_NAME = "PROJECT_NAME"
    HOMEPAGE = "HOMEPAGE"


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
    replace: Optional[list[dict[str, str]]]
    note: Optional[str]