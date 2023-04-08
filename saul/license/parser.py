"""The license generator module for saul.

This module handles parsing license template files.
"""

import os
from typing import Any

import jsonschema
import tomli

from saul.license import License, LicenseInputElement, LicenseReplaceElement


class LicenseParser:
    """Implement the LicenseParser class."""

    MANDATORY_LICENSE_KEYS = ("full_name", "spdx_id", "body")
    MANDATORY_REPLACE_ENTRY_KEYS = ("string", "element")

    LICENSE_TEMPLATE_SCHEMA = {
        "type": "object",
        "properties": {
            "full_name": {"type": "string"},
            "spdx_id": {"type": "string"},
            "body": {"type": "string"},
            "note": {"type": "string"},
            "replace": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "properties": {
                        "string": {"type": "string"},
                        "element": {"type": "string"},
                    },
                    "required": ["string", "element"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["full_name", "spdx_id", "body"],
        "additionalProperties": False,
    }

    def __init__(
        self,
        licenses_dir: str,
    ) -> None:
        """Initialize a LicenseParser.

        :param licenses_dir: directory containing license files (in TOML form),
            containing the body of the license as well as various metadata.
        """
        if not os.path.isdir(licenses_dir):
            raise OSError(f"License directory {licenses_dir} not found.")
        self.__licenses_dir = licenses_dir
        self.__raw_licenses = []

        # Read the raw license templates.
        # They are TOML files, containing metadata and the license body.
        for element in os.listdir(self.__licenses_dir):
            if os.path.isfile(
                os.path.join(self.__licenses_dir, element)
            ) and element.endswith(".toml"):
                with open(
                    os.path.join(self.__licenses_dir, element), "r"
                ) as license_template:
                    self.__raw_licenses.append(
                        (
                            os.path.join(self.__licenses_dir, element),
                            license_template.read(),
                        )
                    )

    def parse_license_templates(self) -> list[License]:
        """Parse license templates from the licenses directory.

        :return: a list of parsed license templates.
        """
        licenses = []

        # Parse the known licenses.
        for raw_license_path, raw_license in self.__raw_licenses:
            try:
                license_dict = tomli.loads(raw_license)
            except tomli.TOMLDecodeError as e:
                raise tomli.TOMLDecodeError(
                    f"Error parsing license file {raw_license_path}: {e}"
                ) from e

            licenses.append(
                self.__parse_license_template(
                    license_dict=license_dict, license_path=raw_license_path
                )
            )

        return licenses

    def __parse_license_template(
        self, license_dict: dict[str, Any], license_path: str
    ) -> License:
        """Parse a license template.

        This method goes through a series of checks regarding the structure of the
        raw license data, in order to make sure that it respects the structure that the
        license generator expects. These checks mainly involve the presence or absence
        of keys in the raw license dict, as well as their types and values.

        :param license_dict: the raw license dict, parsed from the license TOML file.
        :param license_path: the path to the license TOML file.
        :return: a complete License object (if the parsing is successful).
        """
        try:
            jsonschema.validate(
                instance=license_dict, schema=self.LICENSE_TEMPLATE_SCHEMA
            )
        except jsonschema.ValidationError as e:
            raise jsonschema.ValidationError(f"{license_path}: {e}") from e

        replace_elements = []
        for replace_dict in license_dict.get("replace", []):
            try:
                replace_element = LicenseReplaceElement(
                    string=replace_dict["string"],
                    element=LicenseInputElement(replace_dict["element"]),
                )
            except ValueError as e:
                raise ValueError(
                    f"{license_path}: Invalid license input element "
                    f"'{replace_dict['element']}' for 'replace' entry '{replace_dict}'."
                ) from e

            if replace_element.string not in license_dict["body"]:
                raise ValueError(
                    f"{license_path}: Cannot find string '{replace_element.string}' of "
                    f"'replace' entry '{replace_dict}' in license body."
                )

            replace_elements.append(replace_element)

        # All done, we can return the complete license object.
        return License(
            full_name=license_dict["full_name"],
            spdx_id=license_dict["spdx_id"],
            body=license_dict["body"],
            note=license_dict.get("note"),
            replace=replace_elements,
        )
