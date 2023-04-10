"""The configuration module.

This module contains description of the project-level and licence-level configurations
for saul.

A project-level can contain multiple license-level configurations; it is defined either
by a configuration file at the root of the project (see
:attr:`saul.config.parser.SaulConfigParser.CONFIG_FILE_NAME`) or interactively, by
prompting the user for data via stdin.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class SaulLicenseConfig:
    """Implement the license-level configuration for saul.

    This class holds information about a configuration concerning one license.

    :ivar spdx_id: the SPDX ID of the license.
    :ivar license_file: the path to the file the license will be written on.
    :ivar copyright_year_start: the starting year of the copyright of the license.
    :ivar copyright_year_end: the ending year of the copyright of the license.
    :ivar copyright_holders: the names of the holders of the copyright.
    :ivar project_name: the name of the project.
    :ivar organization: the name of the organization in charge of the project.
    :ivar homepage: the homepage of the project.
    """

    spdx_id: str
    license_file: str
    copyright_year_start: str
    copyright_year_end: str
    copyright_holders: Optional[str] = None
    project_name: Optional[str] = None
    organization: Optional[str] = None
    homepage: Optional[str] = None

    def to_dict(self) -> dict[str, str]:
        """Transform the object to a dictionary.

        :return: the object in dictionary form.
        """
        current_year = str(datetime.now().year)

        result = {
            "license": self.spdx_id,
            "file": self.license_file,
        }

        if self.copyright_year_start != current_year:
            result["copyright_year_start"] = self.copyright_year_start
        if self.copyright_year_end != current_year:
            result["copyright_year_end"] = self.copyright_year_end
        if self.copyright_holders is not None:
            result["copyright_holders"] = self.copyright_holders
        if self.project_name is not None:
            result["project_name"] = self.project_name
        if self.organization is not None:
            result["organization"] = self.organization
        if self.homepage is not None:
            result["homepage"] = self.homepage

        return result


@dataclass
class SaulProjectConfig:
    """Implement the project-level configuration for saul.

    This class holds information about a configuration concerning a project, which can
    have one or more license-level configurations.

    :ivar license_configs: the list of license configurations of the project.
    """

    license_configs: list[SaulLicenseConfig]

    def to_dict(self) -> dict[str, Any]:
        """Transform the object to a dictionary.

        :return: the object in dictionary form.
        """
        return {
            "licenses": [
                license_config.to_dict() for license_config in self.license_configs
            ]
        }
