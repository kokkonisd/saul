from saul.license import LicenseGenerator


def test_basic_license(licenses_dir):
    license_generator = LicenseGenerator(licenses_dir)

    assert len(license_generator.known_licenses) == 1
    assert [license_id for license_id in license_generator.known_licenses.keys()][
        0
    ] == "test-license-1.0"

    license = license_generator.known_licenses["test-license-1.0"]
    assert license["full_name"] == "Test License 1.0"
    assert license["spdx_id"] == "Test-License-1.0"
    assert license["body"] == "\n".join(
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
    assert license["replace"] == [
        {"string": "<name>", "element": "COPYRIGHT_HOLDERS"},
        {"string": "<year>", "element": "YEAR_RANGE"},
        {"string": "<project>", "element": "PROJECT_NAME"},
        {"string": "<organization>", "element": "ORGANIZATION"},
        {"string": "<homepage>", "element": "HOMEPAGE"},
    ]
    assert license["note"] == "Don't use this license; it's not very good."

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
