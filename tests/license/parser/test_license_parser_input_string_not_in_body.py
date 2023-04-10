import os
import re

import pytest

from saul.exceptions import LicenseParserError
from saul.license.parser import LicenseParser


def test_license_parser_input_string_not_in_body(test_data_dir: str) -> None:
    """Test running the license parser with a non-existent input string."""
    parser = LicenseParser(test_data_dir)

    with pytest.raises(
        LicenseParserError,
        match=re.escape(
            f"{os.path.join(test_data_dir, 'invalid.toml')}: Cannot find string "
            "'<holders>' of 'replace' entry "
            "'{'string': '<holders>', 'element': 'COPYRIGHT_HOLDERS'}' in license body."
        ),
    ):
        parser.parse_license_templates()
