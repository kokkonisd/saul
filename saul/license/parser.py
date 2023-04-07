"""The license generator module for saul.

This module handles parsing license template files.
"""

import os
from typing import Any

import tomlkit

from saul.license import License, LicenseInputElement


class LicenseParser:
    """Implement the LicenseParser class."""

    MANDATORY_LICENSE_KEYS = ("full_name", "spdx_id", "body")
    MANDATORY_REPLACE_ENTRY_KEYS = ("string", "element")

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
                # Make sure to unwrap the TOMLDocument to end up with Plain Old
                # Python Objects.
                license_dict = tomlkit.loads(raw_license).unwrap()
            except tomlkit.exceptions.TOMLKitError as e:
                raise ValueError(f"Error parsing license file {raw_license_path}: {e}")

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

        def __fail(error_type: type, message: str) -> type:
            """Generate an exception/error with the path to the license file.

            :param error_type: the type of the exception/error to generate.
            :param message: the error message to add to the exception/error.
            :return: the complete exception/error object.
            """
            return error_type(f"{license_path}: {message}")

        # There are some mandatory high-level keys that the license TOML file must have,
        # like the body of the license for example.
        for mandatory_key in self.MANDATORY_LICENSE_KEYS:
            if mandatory_key not in license_dict:
                raise __fail(
                    error_type=KeyError,
                    message=f"Key '{mandatory_key}' missing from license.",
                )
            # All mandatory keys must be strings.
            if not isinstance(license_dict[mandatory_key], str):
                raise __fail(
                    error_type=TypeError,
                    message=(
                        f"Key '{mandatory_key}' must be of type str, not "
                        f"{type(license_dict[mandatory_key]).__name__}."
                    ),
                )

        # We're removing keys from the raw license dict in order to check that we've
        # gotten all keys at the end. See the relevant check near the end of this
        # method.
        full_name = license_dict.pop("full_name")
        spdx_id = license_dict.pop("spdx_id")
        body = license_dict.pop("body")
        note = license_dict.pop("note", None)
        # Note must also be a string if it exists.
        if note:
            if not isinstance(note, str):
                raise __fail(
                    error_type=TypeError,
                    message=(
                        f"Key 'note' must be of type str, not {type(note).__name__}."
                    ),
                )
        replace = license_dict.pop("replace", None)

        # The structure of the license TOML file allows to define replacements to be
        # applied to the license when it is generated. These generally involve some user
        # input, such as the year range of the validity of the license, the name(s) of
        # the copyright holder(s) etc (see the `LicenseInputElement` enum).
        # This key is not mandatory; many license texts are to be used as-is, without
        # any replacements.
        if replace:
            # The 'replace' key should be a list of dictionaries, containig the info of
            # each replacement that should be applied. We call these dictionaries
            # 'entries' here.
            if not isinstance(replace, list):
                raise __fail(
                    error_type=TypeError,
                    message=(
                        "Key 'replace' must be of type list, not "
                        f"{type(replace).__name__}."
                    ),
                )

            for entry in replace:
                if not isinstance(entry, dict):
                    raise __fail(
                        error_type=TypeError,
                        message=(
                            f"Entry '{entry}' of key 'replace' must be of type dict, "
                            f"not {type(entry).__name__}."
                        ),
                    )

                # Entries also define mandatory keys, and we must check their presence.
                for mandatory_key in self.MANDATORY_REPLACE_ENTRY_KEYS:
                    if mandatory_key not in entry:
                        raise __fail(
                            error_type=KeyError,
                            message=(
                                f"Key '{mandatory_key}' missing from 'replace' entry "
                                f"'{entry}'."
                            ),
                        )

                # Any other remaining keys in the entry are invalid, so we should raise
                # an error if they exist.
                remaining_entry_keys = ", ".join(
                    [
                        f"'{key}'"
                        for key in entry.keys()
                        if key not in self.MANDATORY_REPLACE_ENTRY_KEYS
                    ]
                )
                if remaining_entry_keys:
                    raise __fail(
                        error_type=KeyError,
                        message=(
                            f"Unknown keys for 'replace' entry '{entry}': "
                            f"{remaining_entry_keys}."
                        ),
                    )

                # The string to be replaced, defined in the entry, should also exist in
                # the license body.
                if entry["string"] not in body:
                    raise __fail(
                        error_type=ValueError,
                        message=(
                            f"Cannot find string of 'replace' entry '{entry}' in "
                            "license body."
                        ),
                    )

                # The element to replace the entry string with must be a valid
                # `LicenseInputElement`.
                try:
                    LicenseInputElement(entry["element"])
                except ValueError as e:
                    raise __fail(
                        error_type=ValueError,
                        message=(
                            "Invalid license input element for 'replace' entry "
                            f"'{entry}'."
                        ),
                    ) from e

        # If there are any remaining keys in the raw license dict (remember, we've
        # popped off all the valid keys by this point), then they must be invalid.
        if license_dict:
            remaining_license_keys = ", ".join(
                [f"'{key}'" for key in license_dict.keys()]
            )
            raise __fail(
                error_type=KeyError,
                message=f"Unknown keys for license: {remaining_license_keys}.",
            )

        # All done, we can return the complete license object.
        return License(
            full_name=full_name,
            spdx_id=spdx_id,
            body=body,
            note=note,
            replace=replace,
        )
