import os
import re

import pytest

from saul.exceptions import LicenseParserError
from saul.license.parser import LicenseParser


def test_license_parser_invalid_project_dir(test_data_dir: str) -> None:
    """Test running the license parser on an invalid project directory."""
    # Make an empty file to use as an invalid licenses dir.
    not_a_dir = os.path.join(test_data_dir, "not_a_dir.txt")
    with open(not_a_dir, "w") as file:
        file.write("\n")

    with pytest.raises(
        LicenseParserError, match=re.escape(f"Invalid licenses directory {not_a_dir}.")
    ):
        LicenseParser(not_a_dir)
