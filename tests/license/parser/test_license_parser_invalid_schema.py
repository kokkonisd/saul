import os
import re

import pytest

from saul.exceptions import LicenseParserError
from saul.license.parser import LicenseParser


def test_license_parser_invalid_schema(test_data_dir: str) -> None:
    """Test running the license parser on a license template file with invalid schema.

    When a license template file does not adhere to the defined schema, we expect an
    exception to be raised.
    """
    parser = LicenseParser(test_data_dir)

    with pytest.raises(
        LicenseParserError,
        match=re.escape(
            f"{os.path.join(test_data_dir, 'invalid.toml')}: 'body' is a required "
            "property."
        ),
    ):
        parser.parse_license_templates()
