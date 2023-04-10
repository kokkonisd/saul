"""The license generator module for saul.

This module handles generating license files.
"""

from dataclasses import dataclass

from saul.config import SaulLicenseConfig, SaulProjectConfig
from saul.exceptions import LicenseGeneratorError
from saul.license import License, LicenseInputElement


@dataclass
class LicenseGenerator:
    """Implement the LicenseGenerator class.

    :ivar known_licenses: the list of licenses that are known to the generator.
    """

    known_licenses: list[License]

    def generate_licenses(self, project_config: SaulProjectConfig) -> None:
        """Generate license(s) given a specific project configuration.

        The project configuration is expected to be generated by
        :class:`saul.config.parser.SaulConfigParser`.

        :param project_config: the project configuration to use.
        """
        for license_config in project_config.license_configs:
            self.__generate_license(license_config)

    def __generate_license(self, license_config: SaulLicenseConfig) -> None:
        """Generate a license based on a license configuration.

        Generate a license file based on the information provided by the license
        configuration.

        :param license_config: the license configuration.
        """
        _license = self.__get_license_by_spdx_id(license_config.spdx_id)

        body = _license.body
        for replace_element in _license.replace:
            if replace_element.element == LicenseInputElement.COPYRIGHT_YEAR_RANGE:
                if (
                    license_config.copyright_year_start
                    == license_config.copyright_year_end
                ) or not license_config.copyright_year_end:
                    input_element = license_config.copyright_year_start
                else:
                    input_element = (
                        f"{license_config.copyright_year_start}-"
                        f"{license_config.copyright_year_end}"
                    )
            else:
                input_element = getattr(license_config, replace_element.element.value)

            body = body.replace(replace_element.string, input_element)

        try:
            with open(license_config.license_file, "w") as license_file:
                license_file.write(body)
        except Exception as e:
            raise LicenseGeneratorError(
                f"Cannot create license file {license_config.license_file}."
            ) from e

    def __get_license_by_spdx_id(self, spdx_id: str) -> License:
        """Get a License object via an SPDX ID.

        :param spdx_id: the SPDX ID used to identify the License object.
        :return: the corresponding License object.
        """
        matching_licenses = [
            _license
            for _license in self.known_licenses
            if _license.spdx_id.lower() == spdx_id.lower()
        ]
        assert len(matching_licenses) == 1

        return matching_licenses[0]
