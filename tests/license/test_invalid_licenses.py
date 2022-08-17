import os
import tempfile
import pytest
import tomlkit

from saul.license import LicenseGenerator


def parse_license(license_filename, licenses_dir):
    """Parse a license file.

    This function is a helper to facilitate direct calls to the `_parse_license` method.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        license_generator = LicenseGenerator(temp_dir)

        license_path = os.path.join(licenses_dir, license_filename)
        with open(license_path, "r") as license_file:
            raw_license = tomlkit.load(license_file).unwrap()

        license_generator._parse_license(
            raw_license=raw_license, license_path=license_path
        )


def test_invalid_licenses_dir():
    """Test passing an invalid licenses directory to parse from."""
    with pytest.raises(OSError, match=r"License directory foobarbaznotreal not found."):
        LicenseGenerator("foobarbaznotreal")


def test_invalid_toml(licenses_dir):
    """Test parsing a license with invalid TOML code."""
    invalid_toml_dir = os.path.join(
        os.path.abspath(os.path.join(licenses_dir, os.pardir)), "invalid_toml"
    )

    with pytest.raises(
        ValueError,
        match=(
            "Error parsing license file "
            f"{os.path.join(invalid_toml_dir, 'invalid.toml')}:"
        ),
    ):
        LicenseGenerator(invalid_toml_dir)


def test_empty_license(licenses_dir):
    """Test parsing an empty license file."""
    with pytest.raises(
        KeyError, match=r"empty-license\.toml: Key 'full_name' missing from license\."
    ):
        parse_license("empty-license.toml", licenses_dir)


def test_license_missing_body(licenses_dir):
    """Test parsing a license file with no body."""
    with pytest.raises(
        KeyError, match=r"missing-body\.toml: Key 'body' missing from license\."
    ):
        parse_license("missing-body.toml", licenses_dir)


def test_license_missing_spdx_id(licenses_dir):
    """Test parsing a license file with no SPDX ID."""
    with pytest.raises(
        KeyError, match=r"missing-spdx-id\.toml: Key 'spdx_id' missing from license\."
    ):
        parse_license("missing-spdx-id.toml", licenses_dir)


def test_license_missing_full_name(licenses_dir):
    """Test parsing a license file with no full name."""
    with pytest.raises(
        KeyError,
        match=r"missing-full-name\.toml: Key 'full_name' missing from license\.",
    ):
        parse_license("missing-full-name.toml", licenses_dir)


def test_full_name_wrong_type(licenses_dir):
    """Test parsing a license where the 'full_name' key is of the wrong type."""
    with pytest.raises(
        TypeError,
        match=(
            r"full-name-wrong-type\.toml: Key 'full_name' must be of type str, not "
            r"int\."
        ),
    ):
        parse_license("full-name-wrong-type.toml", licenses_dir)


def test_spdx_id_wrong_type(licenses_dir):
    """Test parsing a license where the 'spdx_id' key is of the wrong type."""
    with pytest.raises(
        TypeError,
        match=(
            r"spdx-id-wrong-type\.toml: Key 'spdx_id' must be of type str, not list\."
        ),
    ):
        parse_license("spdx-id-wrong-type.toml", licenses_dir)


def test_body_wrong_type(licenses_dir):
    """Test parsing a license where the 'body' key is of the wrong type."""
    with pytest.raises(
        TypeError,
        match=r"body-wrong-type\.toml: Key 'body' must be of type str, not dict\.",
    ):
        parse_license("body-wrong-type.toml", licenses_dir)


def test_note_wrong_type(licenses_dir):
    """Test parsing a license where the 'note' key is of the wrong type."""
    with pytest.raises(
        TypeError,
        match=r"note-wrong-type\.toml: Key 'note' must be of type str, not float\.",
    ):
        parse_license("note-wrong-type.toml", licenses_dir)


def test_license_replace_wrong_type(licenses_dir):
    """Test parsing a license where the 'replace' key is of the wrong type."""
    with pytest.raises(
        TypeError,
        match=(
            r"replace-wrong-type\.toml: Key 'replace' must be of type list, not str\."
        ),
    ):
        parse_license("replace-wrong-type.toml", licenses_dir)


def test_license_replace_entry_wrong_type(licenses_dir):
    """Test parsing a license where a 'replace' entry is of the wrong type."""
    with pytest.raises(
        TypeError,
        match=(
            r"replace-entry-wrong-type\.toml: Entry '3\.1415' of key 'replace' must be "
            r"of type dict, not float\."
        ),
    ):
        parse_license("replace-entry-wrong-type.toml", licenses_dir)


def test_license_replace_missing_string(licenses_dir):
    """Test parsing a license where a 'replace' entry is missing the 'string' key."""
    with pytest.raises(
        KeyError,
        match=(
            r"replace-missing-string\.toml: Key 'string' missing from 'replace' entry "
            r"'{'element': 'FOO'}'\."
        ),
    ):
        parse_license("replace-missing-string.toml", licenses_dir)


def test_license_replace_missing_element(licenses_dir):
    """Test parsing a license where a 'replace' entry is missing the 'element' key."""
    with pytest.raises(
        KeyError,
        match=(
            r"replace-missing-element\.toml: Key 'element' missing from 'replace' "
            r"entry '{'string': '<foo>'}'\."
        ),
    ):
        parse_license("replace-missing-element.toml", licenses_dir)


def test_license_replace_string_not_in_body(licenses_dir):
    """Test parsing a license where a 'replace' entry has an invalid 'string' key.

    Specifically, the value of the 'string' key is not present in the license body.
    """
    with pytest.raises(
        ValueError,
        match=(
            r"replace-string-not-in-body\.toml: Cannot find string of 'replace' entry "
            r"'{'string': 'notinbody', 'element': 'YEAR_RANGE'}' in license body\."
        ),
    ):
        parse_license("replace-string-not-in-body.toml", licenses_dir)


def test_license_replace_invalid_element(licenses_dir):
    """Test parsing a license where a 'replace' entry has an invalid 'element' key.

    Specifically, the value of the 'element' key is not a valid input element.
    """
    with pytest.raises(
        ValueError,
        match=(
            r"replace-invalid-element\.toml: Invalid license input element for "
            r"'replace' entry '{'string': 'invalid', 'element': 'FOOBARBAZ'}'\."
        ),
    ):
        parse_license("replace-invalid-element.toml", licenses_dir)


def test_license_extra_keys(licenses_dir):
    """Test parsing a license where there are extra (invalid) keys."""
    with pytest.raises(
        KeyError,
        match=(
            r"extra-keys\.toml: Unknown keys for license: 'extra_invalid_key', "
            r"'what_is_this_key'\."
        ),
    ):
        parse_license("extra-keys.toml", licenses_dir)


def test_license_extra_replace_keys(licenses_dir):
    """Test parsing a license where a 'replace' entry has extra (invalid) keys."""
    with pytest.raises(
        KeyError,
        match=(
            r"replace-extra-keys\.toml: Unknown keys for 'replace' entry "
            "'{'string': 'keys', 'element': 'YEAR_RANGE', "
            "'extra_invalid_key': 'invalid', 'what_is_this_key': 'idk'}': "
            r"'extra_invalid_key', 'what_is_this_key'\."
        ),
    ):
        parse_license("replace-extra-keys.toml", licenses_dir)
