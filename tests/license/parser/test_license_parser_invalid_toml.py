import os
import re

import pytest

from saul.exceptions import LicenseParserError
from saul.license.parser import LicenseParser


def test_license_parser_invalid_toml(test_data_dir: str) -> None:
    """Test running the license parser on a license template file with invalid TOML."""
    parser = LicenseParser(test_data_dir)

    with pytest.raises(
        LicenseParserError,
        match=re.escape(
            "Error parsing license file "
            f"{os.path.join(test_data_dir, 'invalid.toml')}: expected a table key, "
            "found an equals at line 1 column 1"
        ),
    ):
        parser.parse_license_templates()
