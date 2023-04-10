import os
import re

import pytest

from saul.config import SaulLicenseConfig, SaulProjectConfig
from saul.exceptions import LicenseGeneratorError
from saul.license import License
from saul.license.generator import LicenseGenerator


def test_license_generator_invalid_license_file(temp_dir: str) -> None:
    """Test running the license generator with an invalid license file."""
    known_licenses = [
        License(
            full_name="Minimal license",
            spdx_id="ML",
            body="This is the minimal license. (c) (year) (holders)\n",
            replace=[],
            note=None,
        )
    ]

    does_not_exist = os.path.join(temp_dir, "does-not-exist", "LICENSE.whoops")
    project_config = SaulProjectConfig(
        [
            SaulLicenseConfig(
                spdx_id="ml",
                license_file=does_not_exist,
                copyright_year_start="2023",
                copyright_year_end="2023",
            )
        ]
    )

    generator = LicenseGenerator(known_licenses)

    with pytest.raises(
        LicenseGeneratorError,
        match=re.escape(f"Cannot create license file {does_not_exist}."),
    ):
        generator.generate_licenses(project_config)
