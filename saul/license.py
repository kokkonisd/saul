from typing import Optional, Any, TypedDict
from enum import Enum
import tomlkit
import os


class LicenseInputElement(Enum):
    """Enumerate all the possible data entries needed to complete a license text."""

    YEAR_RANGE = "YEAR_RANGE"
    COPYRIGHT_HOLDERS = "COPYRIGHT_HOLDERS"
    ORGANIZATION = "ORGANIZATION"
    PROJECT_NAME = "PROJECT_NAME"
    HOMEPAGE = "HOMEPAGE"


class License(TypedDict):
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


class LicenseGenerator:
    """Generate complete licenses."""

    DEFAULT_FILENAME = "LICENSE"
    MANDATORY_LICENSE_KEYS = ("full_name", "spdx_id", "body")
    MANDATORY_REPLACE_ENTRY_KEYS = ("string", "element")

    def __init__(
        self,
        licenses_dir: str,
    ) -> None:
        """Initialize a LicenseGenerator.

        :param licenses_dir: directory containing license files (in TOML form),
            containing the body of the license as well as various metadata.
        """
        if not os.path.isdir(licenses_dir):
            raise OSError(f"License directory {licenses_dir} not found.")
        self.__licenses_dir = licenses_dir
        self.__known_licenses: list[License] = []

        # Parse the known licenses.
        for element in os.listdir(self.__licenses_dir):
            # Licenses are TOML files, containing metadata and the license body.
            if os.path.isfile(
                os.path.join(self.__licenses_dir, element)
            ) and element.endswith(".toml"):
                with open(
                    os.path.join(self.__licenses_dir, element), "r"
                ) as license_file:
                    try:
                        # Make sure to unwrap the TOMLDocument to end up with Plain Old
                        # Python Objects.
                        raw_license = tomlkit.load(license_file).unwrap()
                    except tomlkit.exceptions.TOMLKitError as e:
                        raise ValueError(
                            "Error parsing license file "
                            f"{os.path.join(self.__licenses_dir, element)}: {e}"
                        )

                self.__known_licenses.append(
                    self._parse_license(
                        # TODO: remove the type: ignore when the commit fixing the
                        # return type of tomlkit.toml_document.TOMLDocument.unwrap gets
                        # corrected.
                        # See https://github.com/sdispater/tomlkit/commit/\
                        #             80f958c6b1914735aef61db1d0a045a61fca4eed
                        # for more info.
                        raw_license=raw_license,  # type: ignore
                        license_path=os.path.join(self.__licenses_dir, element),
                    )
                )

    def _parse_license(self, raw_license: dict[str, Any], license_path: str) -> License:
        """Parse a license file, given its raw content (in dict form).

        This method goes through a series of checks regarding the structure of the
        raw license data, in order to make sure that it respects the structure that the
        license generator expects. These checks mainly involve the presence or absence
        of keys in the raw license dict, as well as their types and values.

        :param raw_license: the raw license dict, parsed from the license TOML file.
        :param license_path: the path to the license TOML file.
        :return: a complete License object (if the parsing is successful).
        """

        def LicenseError(error_type: type, message: str) -> type:
            """Generate an exception/error with the path to the license file.

            :param error_type: the type of the exception/error to generate.
            :param message: the error message to add to the exception/error.
            :return: the complete exception/error object.
            """
            return error_type(f"{license_path}: {message}")  # type: ignore

        # There are some mandatory high-level keys that the license TOML file must have,
        # like the body of the license for example.
        for mandatory_key in self.MANDATORY_LICENSE_KEYS:
            if mandatory_key not in raw_license:
                raise LicenseError(
                    error_type=KeyError,
                    message=f"Key '{mandatory_key}' missing from license.",
                )
            # All mandatory keys must be strings.
            if not isinstance(raw_license[mandatory_key], str):
                raise LicenseError(
                    error_type=TypeError,
                    message=(
                        f"Key '{mandatory_key}' must be of type str, not "
                        f"{type(raw_license[mandatory_key]).__name__}."
                    ),
                )

        # We're removing keys from the raw license dict in order to check that we've
        # gotten all keys at the end. See the relevant check near the end of this
        # method.
        full_name = raw_license.pop("full_name")
        spdx_id = raw_license.pop("spdx_id")
        body = raw_license.pop("body")
        note = raw_license.pop("note", None)
        # Note must also be a string if it exists.
        if note:
            if not isinstance(note, str):
                raise LicenseError(
                    error_type=TypeError,
                    message=(
                        f"Key 'note' must be of type str, not {type(note).__name__}."
                    ),
                )
        replace = raw_license.pop("replace", None)

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
                raise LicenseError(
                    error_type=TypeError,
                    message=(
                        "Key 'replace' must be of type list, not "
                        f"{type(replace).__name__}."
                    ),
                )

            for entry in replace:
                if not isinstance(entry, dict):
                    raise LicenseError(
                        error_type=TypeError,
                        message=(
                            f"Entry '{entry}' of key 'replace' must be of type dict, "
                            f"not {type(entry).__name__}."
                        ),
                    )

                # Entries also define mandatory keys, and we must check their presence.
                for mandatory_key in self.MANDATORY_REPLACE_ENTRY_KEYS:
                    if mandatory_key not in entry:
                        raise LicenseError(
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
                    raise LicenseError(
                        error_type=KeyError,
                        message=(
                            f"Unknown keys for 'replace' entry '{entry}': "
                            f"{remaining_entry_keys}."
                        ),
                    )

                # The string to be replaced, defined in the entry, should also exist in
                # the license body.
                if entry["string"] not in body:
                    raise LicenseError(
                        error_type=ValueError,
                        message=(
                            f"Cannot find string of entry '{entry}' in license body."
                        ),
                    )

                # The element to replace the entry string with must be a valid
                # `LicenseInputElement`.
                try:
                    LicenseInputElement(entry["element"])
                except ValueError as e:
                    raise LicenseError(
                        error_type=ValueError,
                        message=f"Invalid license input element for entry '{entry}'.",
                    ) from e

        # If there are any remaining keys in the raw license dict (remember, we've
        # popped off all the valid keys by this point), then they must be invalid.
        if raw_license:
            remaining_license_keys = ", ".join(
                [f"'{key}'" for key in raw_license.keys()]
            )
            raise LicenseError(
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

    @property
    def known_licenses(self):
        """Get the list of known license file IDs and full names."""
        return {
            license["spdx_id"].lower(): license for license in self.__known_licenses
        }

    def generate_license(
        self,
        license_id: str,
        interactive: bool = False,
        year_range: Optional[str] = None,
        copyright_holders: Optional[str] = None,
        organization: Optional[str] = None,
        project_name: Optional[str] = None,
        homepage: Optional[str] = None,
        from_cli: bool = False,
    ) -> tuple[str, str]:
        """Generate a license.

        This method generates a license either in a file or in STDOUT based on the
        input. It also can handle both values from arguments and interactive mode, in
        which case it will itself seek input from the user.
        Note that while the full range of input elements can be passed to this method,
        only the necessary input elements will be used. For example, GPL-3.0 does not
        require any input, so if any input is passed it will simply be ignored.

        :param license_id: the ID of the license to generate. Must be present in
            `self.known_licenses` when this method is called.
        :param interactive: if True, then ask the user for input manually. Else, use the
            input provided by the other arguments.
        :param year_range: the year range covering the copyright of the license (e.g.
            '1996-2025').
        :param copyright_holders: the names and emails of the copyright holders (e.g.
            'John Doe (jdoe@foo.com)').
        :param organization: the name of the organization supporting the work covered by
            the license (e.g. 'Foo Inc.').
        :param project_name: the name of the project covered by the license.
        :param homepage: the homepage/website of the project.
        :param from_cli: if True, error reporting will be modified to output missing
            values as CLI switches/arguments.
        :return: a tuple containing the final body of the license and any note(s)
            accompanying it.
        """
        if license_id not in self.known_licenses:
            raise ValueError(f"Unknown license ID '{license_id}'.")

        input_element_map: dict[LicenseInputElement, Optional[str]] = {}

        if interactive:
            input_element_map = {
                LicenseInputElement.YEAR_RANGE: "Year range? (example: 1999-2020)",
                LicenseInputElement.COPYRIGHT_HOLDERS: (
                    "Copyright holder(s)? (example: John Doe (doe@foo.com), Jane Doe "
                    "(doe2@foo.com))"
                ),
                LicenseInputElement.ORGANIZATION: "Organization? (example: Foo Inc.)",
                LicenseInputElement.PROJECT_NAME: "Project name? (example: foo-cli)",
                LicenseInputElement.HOMEPAGE: "Homepage? (example: www.foo.com)",
            }
        else:
            input_element_map = {
                LicenseInputElement.YEAR_RANGE: year_range,
                LicenseInputElement.COPYRIGHT_HOLDERS: copyright_holders,
                LicenseInputElement.ORGANIZATION: organization,
                LicenseInputElement.PROJECT_NAME: project_name,
                LicenseInputElement.HOMEPAGE: homepage,
            }

        license = self.known_licenses[license_id]

        license_body = license["body"]

        if license["replace"]:
            for entry in license["replace"]:
                string = entry["string"]
                element = entry["element"]
                input_element = LicenseInputElement(element)
                input_source = input_element_map[input_element]

                if interactive:
                    input_value = input(f"{input_source}> ").strip()
                else:
                    if input_source is None:
                        missing_input = input_element.value.lower()
                        if from_cli:
                            missing_input = f"--{missing_input.replace('_', '-')}"
                        raise ValueError(
                            f"'{missing_input}' is required for the "
                            f"{license['spdx_id']} license."
                        )

                    input_value = input_source

                license_body = license_body.replace(string, input_value)

        return license_body, license["note"]
