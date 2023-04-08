"""The license generator module for saul.

This module handles generating license files.
"""

from dataclasses import dataclass
from typing import Optional

from saul.license import License, LicenseInputElement


@dataclass
class LicenseGenerator:
    """Implement the LicenseGenerator class."""

    licenses: list[License]
    DEFAULT_FILENAME = "LICENSE"

    @property
    def known_licenses(self):
        """Get the list of known license file IDs and full names."""
        return {_license.spdx_id.lower(): _license for _license in self.licenses}

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

        _license = self.known_licenses[license_id]

        license_body = _license.body

        if _license.replace:
            for entry in _license.replace:
                string = entry.string
                input_element = entry.element
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
                            f"{_license.spdx_id} license."
                        )

                    input_value = input_source

                license_body = license_body.replace(string, input_value)

        return license_body, _license.note
