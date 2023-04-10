import os

from saul.config import SaulLicenseConfig, SaulProjectConfig
from saul.license import License, LicenseInputElement, LicenseReplaceElement
from saul.license.generator import LicenseGenerator


def test_license_generator_basic_license(temp_dir: str) -> None:
    """Test running the license generator with basic licenses."""
    known_licenses = [
        License(
            full_name="Minimal license",
            spdx_id="ML",
            body="This is the minimal license. (c) (year) (holders)\n",
            replace=[
                LicenseReplaceElement(
                    string="(year)", element=LicenseInputElement.COPYRIGHT_YEAR_RANGE
                ),
                LicenseReplaceElement(
                    string="(holders)", element=LicenseInputElement.COPYRIGHT_HOLDERS
                ),
            ],
            note=None,
        ),
        License(
            full_name="Extra license",
            spdx_id="XTRA",
            body="This license is so extra! (c) <y> <h> <o> <p> <s>\n",
            replace=[
                LicenseReplaceElement(
                    string="<y>", element=LicenseInputElement.COPYRIGHT_YEAR_RANGE
                ),
                LicenseReplaceElement(
                    string="<h>", element=LicenseInputElement.COPYRIGHT_HOLDERS
                ),
                LicenseReplaceElement(
                    string="<o>", element=LicenseInputElement.ORGANIZATION
                ),
                LicenseReplaceElement(
                    string="<p>", element=LicenseInputElement.PROJECT_NAME
                ),
                LicenseReplaceElement(
                    string="<s>", element=LicenseInputElement.HOMEPAGE
                ),
            ],
            note="It also has a note!",
        ),
    ]

    project_config = SaulProjectConfig(
        [
            SaulLicenseConfig(
                spdx_id="ml",
                license_file=os.path.join(temp_dir, "LICENSE.ML"),
                copyright_year_start="2023",
                copyright_year_end="2023",
                copyright_holders="Holders",
            ),
            SaulLicenseConfig(
                spdx_id="xtra",
                license_file=os.path.join(temp_dir, "LICENSE.XTRA"),
                copyright_year_start="2000",
                copyright_year_end="3000",
                copyright_holders="C. H. Older",
                project_name="The Project",
                organization="The Org",
                homepage="site.com",
            ),
        ]
    )

    generator = LicenseGenerator(known_licenses)
    generator.generate_licenses(project_config)

    # There should be a LICENSE.ML file.
    license_ml_file = os.path.join(temp_dir, "LICENSE.ML")
    assert os.path.isfile(license_ml_file)
    # It should contain the generated license.
    with open(license_ml_file, "r") as file:
        license_ml_data = file.read()
    # Since the start and end years are the same for the copyright, they should be
    # merged into one (i.e., not 2023-2023).
    assert license_ml_data == "This is the minimal license. (c) 2023 Holders\n"

    # There should be a LICENSE.XTRA file.
    license_xtra_file = os.path.join(temp_dir, "LICENSE.XTRA")
    assert os.path.isfile(license_xtra_file)
    # It should contain the generated license.
    with open(license_xtra_file, "r") as file:
        license_xtra_data = file.read()
    # Since the start and end years are the same for the copyright, they should be
    # merged into one (i.e., not 2023-2023).
    assert license_xtra_data == (
        "This license is so extra! (c) 2000-3000 C. H. Older The Org The Project "
        "site.com\n"
    )
