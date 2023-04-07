from saul.license.generator import LicenseGenerator
from saul.license.parser import LicenseParser


def test_basic_license(licenses_dir):
    """Test parsing a license."""
    license_parser = LicenseParser(licenses_dir)
    licenses = license_parser.parse_license_templates()

    assert len(licenses) == 1
    _license = licenses[0]

    assert _license.full_name == "Test License 1.0"
    assert _license.spdx_id == "Test-License-1.0"
    assert _license.body == "\n".join(
        [
            "    TEST LICENSE 1.0",
            "--------------------",
            "",
            "This license proves that <project> by <organization> is the best.",
            "You can find it on <homepage>.",
            "",
            "(C) <name> <year>",
            "",
        ]
    )
    assert _license.replace == [
        {"string": "<name>", "element": "COPYRIGHT_HOLDERS"},
        {"string": "<year>", "element": "YEAR_RANGE"},
        {"string": "<project>", "element": "PROJECT_NAME"},
        {"string": "<organization>", "element": "ORGANIZATION"},
        {"string": "<homepage>", "element": "HOMEPAGE"},
    ]
    assert _license.note == "Don't use this license; it's not very good."


def test_generate_basic_license(licenses_dir):
    """Test generating a license."""
    license_parser = LicenseParser(licenses_dir)
    licenses = license_parser.parse_license_templates()
    license_generator = LicenseGenerator(licenses)

    """Test generating a license."""
    license_body, license_note = license_generator.generate_license(
        license_id="test-license-1.0",
        year_range="1800-1900",
        copyright_holders="me (me@myhouse.com)",
        organization="the cool devs",
        project_name="a thing we did",
        homepage="https://www.thecooldevs.com/athingwedid",
    )
    assert license_body == "\n".join(
        [
            "    TEST LICENSE 1.0",
            "--------------------",
            "",
            "This license proves that a thing we did by the cool devs is the best.",
            "You can find it on https://www.thecooldevs.com/athingwedid.",
            "",
            "(C) me (me@myhouse.com) 1800-1900",
            "",
        ]
    )
    assert license_note == "Don't use this license; it's not very good."
