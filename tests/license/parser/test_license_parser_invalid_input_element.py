import os
import re

import pytest

from saul.exceptions import LicenseParserError
from saul.license.parser import LicenseParser


def test_license_parser_invalid_input_element(test_data_dir: str) -> None:
    """Test running the license parser with invalid input elements."""
    parser = LicenseParser(test_data_dir)

    with pytest.raises(
        LicenseParserError,
        match=re.escape(
            f"{os.path.join(test_data_dir, 'invalid.toml')}: Invalid license input "
            "element 'WHAT_IS_THIS_ELEMENT' for 'replace' entry "
            "'{'string': '!', 'element': 'WHAT_IS_THIS_ELEMENT'}'."
        ),
    ):
        parser.parse_license_templates()
