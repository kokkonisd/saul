from saul.license import License, LicenseInputElement, LicenseReplaceElement
from saul.license.parser import LicenseParser


def test_license_parser_basic_license(test_data_dir: str) -> None:
    """Test running the license parser on basic license templates."""
    parser = LicenseParser(test_data_dir)

    expected_license_templates = [
        License(
            full_name="Minimal license",
            spdx_id="ML",
            body="This is the minimal license.\n",
            replace=[],
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

    actual_license_templates = parser.parse_license_templates()

    assert sorted(
        actual_license_templates, key=lambda _license: _license.spdx_id
    ) == sorted(expected_license_templates, key=lambda _license: _license.spdx_id)
