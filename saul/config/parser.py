"""The configuration parser module.

This module contains the parser for the project- and license-level configurations for
saul.

Also see :mod:`saul.config`.
"""

import os
from datetime import datetime
from typing import NoReturn, Optional, Type

import jsonschema
import rtoml

from saul.config import SaulLicenseConfig, SaulProjectConfig
from saul.exceptions import (
    MissingInputElementError,
    SaulConfigError,
    UnknownLicenseError,
)
from saul.license import License, LicenseInputElement


class SaulConfigParser:
    """Implement the SaulConfigParser class.

    This class offers functionality to parse and configure saul.

    :cvar CONFIG_SCHEMA: the JSON Schema that the configuration must follow.
    :cvar CONFIG_FILE_NAME: the name of the configuration file.
    :cvar DEFAULT_LICENSE_FILE_NAME: the name of the default license file.
    """

    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "licenses": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "properties": {
                        "license": {"type": "string"},
                        "file": {"type": "string"},
                        "copyright_holders": {"type": "string"},
                        "copyright_year_start": {"type": "string"},
                        "copyright_year_end": {"type": "string"},
                        "organization": {"type": "string"},
                        "project_name": {"type": "string"},
                        "homepage": {"type": "string"},
                    },
                    "required": ["license"],
                },
            }
        },
        "required": ["licenses"],
        "additionalProperties": False,
    }

    CONFIG_FILE_NAME = ".saul"

    DEFAULT_LICENSE_FILE_NAME = "LICENSE"

    def __init__(self, project_dir: str, known_licenses: list[License]) -> None:
        """Initialize the config parser.

        :param project_dir: the project directory. This is used to look for a
            configuration file.
        :param known_licenses: the list of licenses that are known to the configuration
            parser.
        """
        self.__project_dir = os.path.abspath(project_dir)
        self.__known_licenses = known_licenses
        self.__config_file: Optional[str] = None

    @property
    def project_dir(self) -> str:
        """Get the project directory associated with the configuration parser.

        :return: the absolute path to the project directory.
        """
        return self.__project_dir

    def __fail(
        self,
        error: Type[Exception],
        message: str,
        base_error: Optional[Type[Exception]] = None,
    ) -> NoReturn:
        """Report an error message by raising an exception.

        :param error: the type of exception to raise.
        :param message: the message to attach to the exception.
        :param base_error: the error that resulted in this exception being raised (if
            any).
        """
        raise error(f"{self.__config_file}: {message}") from base_error

    def parse_config(self) -> SaulProjectConfig:
        """Parse a project configuration.

        If a configuration file exists, then parse the configuration from it; otherwise,
        get the configuration interactively from the user via stdin.

        :return: the project configuration.
        """
        self.__config_file = os.path.join(self.__project_dir, self.CONFIG_FILE_NAME)

        if not os.path.isfile(self.__config_file):
            self.__config_file = "<stdin>"
            return self.__parse_config_interactively()

        return self.__parse_config_from_file(self.__config_file)

    def __parse_config_from_file(self, config_file: str) -> SaulProjectConfig:
        """Parse a project configuration from a configuration file.

        Project configuration files are TOML files; they are expected to follow a schema
        described in :attr:`saul.config.parser.SaulConfigParser.CONFIG_SCHEMA`.

        :param config_file: the configuration file to parse.
        :return: the resulting project configuration.
        """
        current_year = str(datetime.now().year)

        with open(config_file, "r") as file:
            try:
                config_dict = rtoml.loads(file.read())
            except rtoml.TomlParsingError as e:
                message = str(e).capitalize() + "."
                self.__fail(error=SaulConfigError, message=message, base_error=e)

        try:
            jsonschema.validate(instance=config_dict, schema=self.CONFIG_SCHEMA)
        except jsonschema.ValidationError as e:
            message = str(e).split("\n")[0].capitalize() + "."
            self.__fail(error=SaulConfigError, message=message, base_error=e)

        license_configs = []
        for license_dict in config_dict["licenses"]:
            config = SaulLicenseConfig(
                spdx_id=license_dict["license"],
                license_file=os.path.join(
                    self.project_dir,
                    license_dict.get("file", self.DEFAULT_LICENSE_FILE_NAME),
                ),
                copyright_holders=license_dict.get("copyright_holders"),
                copyright_year_start=license_dict.get(
                    "copyright_year_start", current_year
                ),
                copyright_year_end=license_dict.get("copyright_year_end", current_year),
                organization=license_dict.get("organization"),
                project_name=license_dict.get("project_name"),
                homepage=license_dict.get("homepage"),
            )

            self.__validate_license_config(config)
            license_configs.append(config)

        return SaulProjectConfig(license_configs)

    def __parse_config_interactively(self) -> SaulProjectConfig:
        """Parse a project configuration interactively.

        A project configuration will be parsed via stdin after prompting the user for
        project configuration data.
        Some attributes of the project configuration have default values, so if nothing
        is provided by the user, the default values will be taken.

        :return: the resulting project configuration.
        """
        current_year = str(datetime.now().year)

        spdx_id = input("License (SPDX ID)?> ")
        license_file = (
            input("License file?[default: LICENSE]> ") or self.DEFAULT_LICENSE_FILE_NAME
        )
        copyright_holders = input("Copyright holder(s)?> ") or None
        copyright_year_start = (
            input(f"Copyright year start?[default: {current_year}]> ") or current_year
        )
        copyright_year_end = (
            input(f"Copyright year end?[default: {current_year}]> ") or current_year
        )
        project_name = input("Project name?> ") or None
        organization = input("Organization?> ") or None
        homepage = input("Homepage?> ") or None

        config = SaulLicenseConfig(
            spdx_id=spdx_id,
            license_file=os.path.join(self.project_dir, license_file),
            copyright_holders=copyright_holders,
            copyright_year_start=copyright_year_start,
            copyright_year_end=copyright_year_end,
            project_name=project_name,
            organization=organization,
            homepage=homepage,
        )

        self.__validate_license_config(config)

        project_config = SaulProjectConfig([config])

        print("----")
        generate_config_file_raw_input = input(
            "Save these settings in a config file (`.saul`)?[default: y]> "
        ).lower()
        if not generate_config_file_raw_input:
            generate_config_file = True
        else:
            generate_config_file = generate_config_file_raw_input.startswith("y")

        if generate_config_file:
            self.__config_file = os.path.join(self.__project_dir, self.CONFIG_FILE_NAME)
            with open(self.__config_file, "w") as config_file:
                config_file.write(rtoml.dumps(project_config.to_dict()))

        return project_config

    def __validate_license_config(self, config: SaulLicenseConfig) -> None:
        """Validate a license configuration.

        Validate a license configuration by checking that the license ID exists in the
        known licenses and that all the required input fields of the license have been
        provided.
        An exception will be raised if the license configuration is invalid.
        """
        # Check that the chosen license is valid.
        matching_licenses = [
            _license
            for _license in self.__known_licenses
            if _license.spdx_id.lower() == config.spdx_id.lower()
        ]

        if not matching_licenses:
            self.__fail(
                error=UnknownLicenseError,
                message=(
                    f"Unknown license '{config.spdx_id}'. Run `saul list` to get a "
                    "full list of available licenses."
                ),
            )

        assert len(matching_licenses) == 1
        _license = matching_licenses[0]

        # Check that the fields required by the license are filled in.
        for replace_element in _license.replace:
            input_element = replace_element.element.value

            if replace_element.element == LicenseInputElement.COPYRIGHT_YEAR_RANGE:
                input_element = "copyright_year_start"

            if getattr(config, input_element) is None:
                self.__fail(
                    error=MissingInputElementError,
                    message=f"Missing license input element: '{input_element}'.",
                )
