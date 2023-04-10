import tempfile
from typing import Generator

import pytest

from saul.config.parser import SaulConfigParser
from saul.license.parser import LicenseParser


@pytest.fixture()
def config_parser(test_data_dir: str) -> Generator:
    """Generate a config parser for a given test.

    This fixture assumes that a directory with the same name as the test exists; that
    directory is used as the "license directory", containing all the license template
    files.

    :return: a config parser. Note that the project directory attached to the config
        parser is a temporary directory.
    """
    license_parser = LicenseParser(licenses_dir=test_data_dir)
    licenses = license_parser.parse_license_templates()

    with tempfile.TemporaryDirectory() as project_dir:
        config_parser = SaulConfigParser(
            project_dir=project_dir, known_licenses=licenses
        )

        yield config_parser
