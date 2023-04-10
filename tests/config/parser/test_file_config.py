import datetime
import os
import re
from typing import Any

import pytest

from saul.config import SaulLicenseConfig
from saul.config.parser import SaulConfigParser
from saul.exceptions import (
    MissingInputElementError,
    SaulConfigError,
    UnknownLicenseError,
)


def test_file_config_minimal_licenses(
    monkeypatch: Any, config_parser: SaulConfigParser
) -> None:
    """Test loading a config from a file containing multiple licenses."""
    config_file_contents = "\n".join(
        [
            "[[licenses]]",
            'license = "minimal"',
            'file = "TEST.LICENSE"',
            "copyright_holders = \"Jane 'badass' Doe\"",
            'copyright_year_start = "1982"',
            'copyright_year_end = "2037"',
            'project_name = "Cool Project"',
            'organization = "Nobody"',
            'homepage = "nobody.home"',
            "",
            "[[licenses]]",
            'license = "minimal"',
            'file = "COPYING.ME"',
            'copyright_holders = "IDK!"',
            'copyright_year_start = "2002"',
            'copyright_year_end = ""',
            'project_name = "Cool Project"',
            'organization = "Nobody"',
            'homepage = "nobody.home"',
        ]
    )

    # Write the config file in the project directory.
    with open(
        os.path.join(config_parser.project_dir, config_parser.CONFIG_FILE_NAME), "w"
    ) as config_file:
        config_file.write(config_file_contents)

    project_config = config_parser.parse_config()

    expected_license_configs = [
        SaulLicenseConfig(
            spdx_id="minimal",
            license_file=os.path.join(config_parser.project_dir, "TEST.LICENSE"),
            copyright_holders="Jane 'badass' Doe",
            copyright_year_start="1982",
            copyright_year_end="2037",
            project_name="Cool Project",
            organization="Nobody",
            homepage="nobody.home",
        ),
        SaulLicenseConfig(
            spdx_id="minimal",
            license_file=os.path.join(config_parser.project_dir, "COPYING.ME"),
            copyright_holders="IDK!",
            copyright_year_start="2002",
            copyright_year_end="",
            project_name="Cool Project",
            organization="Nobody",
            homepage="nobody.home",
        ),
    ]

    assert project_config.license_configs == expected_license_configs


def test_file_config_default_values(
    monkeypatch: Any, config_parser: SaulConfigParser
) -> None:
    """Test loading a config from a file with all the values left to their defaults."""
    # "Hardcode" the year to 2023 so that the test is not impacted by the current year.
    monkeypatch.setattr(datetime, "datetime", datetime.datetime(2023, 1, 1, 0, 0, 0))

    config_file_contents = "\n".join(
        [
            "[[licenses]]",
            'license = "minimal"',
        ]
    )

    # Write the config file in the project directory.
    with open(
        os.path.join(config_parser.project_dir, config_parser.CONFIG_FILE_NAME), "w"
    ) as config_file:
        config_file.write(config_file_contents)

    project_config = config_parser.parse_config()

    expected_license_configs = [
        SaulLicenseConfig(
            spdx_id="minimal",
            license_file=os.path.join(
                config_parser.project_dir, config_parser.DEFAULT_LICENSE_FILE_NAME
            ),
            copyright_holders=None,
            copyright_year_start="2023",
            copyright_year_end="2023",
            project_name=None,
            organization=None,
            homepage=None,
        )
    ]

    assert project_config.license_configs == expected_license_configs


def test_file_config_with_syntax_error(config_parser: SaulConfigParser) -> None:
    """Test loading a config from a file with a syntax error."""
    config_file_contents = "\n".join(
        [
            "[[licenses]",
            'license = "minimal"',
        ]
    )

    # Write the config file in the project directory.
    config_file_path = os.path.join(
        config_parser.project_dir, config_parser.CONFIG_FILE_NAME
    )
    with open(config_file_path, "w") as config_file:
        config_file.write(config_file_contents)

    with pytest.raises(
        SaulConfigError,
        match=re.escape(
            f"{config_file_path}: Expected a right bracket, found a newline at line 1 "
            "column 12."
        ),
    ):
        config_parser.parse_config()


def test_file_config_with_incorrect_schema(config_parser: SaulConfigParser) -> None:
    """Test loading a config from a file with incorrect schema."""
    config_file_contents = "\n".join(
        [
            'license = "minimal"',
        ]
    )

    # Write the config file in the project directory.
    config_file_path = os.path.join(
        config_parser.project_dir, config_parser.CONFIG_FILE_NAME
    )
    with open(config_file_path, "w") as config_file:
        config_file.write(config_file_contents)

    with pytest.raises(
        SaulConfigError,
        match=re.escape(f"{config_file_path}: 'licenses' is a required property."),
    ):
        config_parser.parse_config()


def test_file_config_unknown_license(config_parser: SaulConfigParser) -> None:
    """Test loading a config from a file with an unknown license."""
    config_file_contents = "\n".join(
        [
            "[[licenses]]",
            'license = "what_is_this_license"',
        ]
    )

    # Write the config file in the project directory.
    config_file_path = os.path.join(
        config_parser.project_dir, config_parser.CONFIG_FILE_NAME
    )
    with open(config_file_path, "w") as config_file:
        config_file.write(config_file_contents)

    with pytest.raises(
        UnknownLicenseError,
        match=re.escape(
            f"{config_file_path}: Unknown license 'what_is_this_license'. Run `saul "
            "list` to get a full list of available licenses."
        ),
    ):
        config_parser.parse_config()


@pytest.mark.parametrize(
    "config_file_contents,missing_element",
    [
        pytest.param(
            "\n".join(
                [
                    "[[licenses]]",
                    'license = "needs_copyright_holders"',
                ]
            ),
            "copyright_holders",
            id="missing_copyright_holders",
        ),
        pytest.param(
            "\n".join(
                [
                    "[[licenses]]",
                    'license = "needs_project_name"',
                ]
            ),
            "project_name",
            id="missing_project_name",
        ),
        pytest.param(
            "\n".join(
                [
                    "[[licenses]]",
                    'license = "needs_organization"',
                ]
            ),
            "organization",
            id="missing_organization",
        ),
        pytest.param(
            "\n".join(
                [
                    "[[licenses]]",
                    'license = "needs_homepage"',
                ]
            ),
            "homepage",
            id="missing_homepage",
        ),
    ],
)
def test_file_config_missing_input_element(
    config_parser: SaulConfigParser, config_file_contents: str, missing_element: str
) -> None:
    """Test loading a config from a file without providing a required input element."""
    # Write the config file in the project directory.
    config_file_path = os.path.join(
        config_parser.project_dir, config_parser.CONFIG_FILE_NAME
    )
    with open(config_file_path, "w") as config_file:
        config_file.write(config_file_contents)

    with pytest.raises(
        MissingInputElementError,
        match=re.escape(
            f"{config_file_path}: Missing license input element: '{missing_element}'."
        ),
    ):
        config_parser.parse_config()
