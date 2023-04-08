import os
import re
import tempfile

import jsonschema
import pytest
import tomli

from saul.license.parser import LicenseParser


def parse_license(license_filename, licenses_dir):
    """Parse a license file.

    This function is a helper to facilitate direct calls to the `_parse_license` method.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        license_parser = LicenseParser(temp_dir)
        license_path = os.path.join(licenses_dir, license_filename)
        with open(license_path, "r") as license_file:
            license_dict = tomli.loads(license_file.read())

        # Mypy does not track private attribute name mangling, so we're forced to go
        # through `getattr()`.
        parse = getattr(license_parser, "_LicenseParser__parse_license_template")
        parse(license_dict=license_dict, license_path=license_path)


def test_invalid_licenses_dir():
    """Test passing an invalid licenses directory to parse from."""
    with pytest.raises(OSError, match=r"License directory foobarbaznotreal not found."):
        LicenseParser("foobarbaznotreal")


def test_invalid_toml(licenses_dir):
    """Test parsing a license with invalid TOML code."""
    invalid_toml_dir = os.path.join(
        os.path.abspath(os.path.join(licenses_dir, os.pardir)), "invalid_toml"
    )
    license_parser = LicenseParser(invalid_toml_dir)

    with pytest.raises(
        tomli.TOMLDecodeError,
        match=re.escape(
            "Error parsing license file "
            f"{os.path.join(invalid_toml_dir, 'invalid.toml')}:"
        ),
    ):
        license_parser.parse_license_templates()


def test_empty_license(licenses_dir):
    """Test parsing an empty license file."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'empty-license.toml')}: 'full_name' is a "
            "required property"
        ),
    ):
        parse_license("empty-license.toml", licenses_dir)


def test_license_missing_body(licenses_dir):
    """Test parsing a license file with no body."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'missing-body.toml')}: 'body' is a required "
            "property"
        ),
    ):
        parse_license("missing-body.toml", licenses_dir)


def test_license_missing_spdx_id(licenses_dir):
    """Test parsing a license file with no SPDX ID."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'missing-spdx-id.toml')}: 'spdx_id' is a "
            "required property"
        ),
    ):
        parse_license("missing-spdx-id.toml", licenses_dir)


def test_license_missing_full_name(licenses_dir):
    """Test parsing a license file with no full name."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'missing-full-name.toml')}: 'full_name' is a "
            "required property"
        ),
    ):
        parse_license("missing-full-name.toml", licenses_dir)


def test_full_name_wrong_type(licenses_dir):
    """Test parsing a license where the 'full_name' key is of the wrong type."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'full-name-wrong-type.toml')}: 3 is not of "
            "type 'string'"
        ),
    ):
        parse_license("full-name-wrong-type.toml", licenses_dir)


def test_spdx_id_wrong_type(licenses_dir):
    """Test parsing a license where the 'spdx_id' key is of the wrong type."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'spdx-id-wrong-type.toml')}: "
            "[\"this isn't right\"] is not of type 'string'"
        ),
    ):
        parse_license("spdx-id-wrong-type.toml", licenses_dir)


def test_body_wrong_type(licenses_dir):
    """Test parsing a license where the 'body' key is of the wrong type."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'body-wrong-type.toml')}: "
            "{'text': 'wrong type'} is not of type 'string'"
        ),
    ):
        parse_license("body-wrong-type.toml", licenses_dir)


def test_note_wrong_type(licenses_dir):
    """Test parsing a license where the 'note' key is of the wrong type."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'note-wrong-type.toml')}: 2.34 is not of "
            "type 'string'"
        ),
    ):
        parse_license("note-wrong-type.toml", licenses_dir)


def test_license_replace_wrong_type(licenses_dir):
    """Test parsing a license where the 'replace' key is of the wrong type."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'replace-wrong-type.toml')}: 'aaa' is not of "
            "type 'array'"
        ),
    ):
        parse_license("replace-wrong-type.toml", licenses_dir)


def test_license_replace_entry_wrong_type(licenses_dir):
    """Test parsing a license where a 'replace' entry is of the wrong type."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'replace-entry-wrong-type.toml')}: 3.1415 is "
            "not of type 'object'"
        ),
    ):
        parse_license("replace-entry-wrong-type.toml", licenses_dir)


def test_license_replace_missing_string(licenses_dir):
    """Test parsing a license where a 'replace' entry is missing the 'string' key."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'replace-missing-string.toml')}: 'string' is "
            "a required property"
        ),
    ):
        parse_license("replace-missing-string.toml", licenses_dir)


def test_license_replace_missing_element(licenses_dir):
    """Test parsing a license where a 'replace' entry is missing the 'element' key."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'replace-missing-element.toml')}: 'element' "
            "is a required property"
        ),
    ):
        parse_license("replace-missing-element.toml", licenses_dir)


def test_license_replace_string_not_in_body(licenses_dir):
    """Test parsing a license where a 'replace' entry has an invalid 'string' key.

    Specifically, the value of the 'string' key is not present in the license body.
    """
    with pytest.raises(
        ValueError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'replace-string-not-in-body.toml')}: Cannot "
            "find string 'notinbody' of 'replace' entry '{'string': 'notinbody', "
            "'element': 'YEAR_RANGE'}' in license body."
        ),
    ):
        parse_license("replace-string-not-in-body.toml", licenses_dir)


def test_license_replace_invalid_element(licenses_dir):
    """Test parsing a license where a 'replace' entry has an invalid 'element' key.

    Specifically, the value of the 'element' key is not a valid input element.
    """
    with pytest.raises(
        ValueError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'replace-invalid-element.toml')}: Invalid "
            "license input element 'FOOBARBAZ' for 'replace' entry '{'string': "
            "'invalid', 'element': 'FOOBARBAZ'}'."
        ),
    ):
        parse_license("replace-invalid-element.toml", licenses_dir)


def test_license_extra_keys(licenses_dir):
    """Test parsing a license where there are extra (invalid) keys."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'extra-keys.toml')}: Additional properties "
            "are not allowed ('extra_invalid_key', 'what_is_this_key' were unexpected)"
        ),
    ):
        parse_license("extra-keys.toml", licenses_dir)


def test_license_extra_replace_keys(licenses_dir):
    """Test parsing a license where a 'replace' entry has extra (invalid) keys."""
    with pytest.raises(
        jsonschema.ValidationError,
        match=re.escape(
            f"{os.path.join(licenses_dir, 'replace-extra-keys.toml')}: Additional "
            "properties are not allowed ('extra_invalid_key', 'what_is_this_key' were "
            "unexpected)"
        ),
    ):
        parse_license("replace-extra-keys.toml", licenses_dir)
