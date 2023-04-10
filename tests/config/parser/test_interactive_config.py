import datetime
import os
import re
from typing import Any

import pytest

from saul.config import SaulLicenseConfig
from saul.config.parser import SaulConfigParser
from saul.exceptions import MissingInputElementError, UnknownLicenseError


@pytest.mark.parametrize(
    "save_config",
    [
        pytest.param("y", id="with_explicit_save"),
        pytest.param("", id="with_implicit_save"),
        pytest.param("n", id="without_save"),
    ],
)
def test_interactive_config_save(
    monkeypatch: Any, config_parser: SaulConfigParser, save_config: str
) -> None:
    """Test running an interactive configuration with/without saving it."""
    # Provide input to the interactive configuration.
    interactive_input = iter(
        [
            "minimal",
            "MY.LICENSE",
            "John 'foo' Doe",
            "1999",
            "2002",
            "The Project",
            "Foobar Org.",
            "foobar.project.org",
            save_config,
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(interactive_input))
    # "Hardcode" the year to 2023 so that the test is not impacted by the current year.
    monkeypatch.setattr(datetime, "datetime", datetime.datetime(2023, 1, 1, 0, 0, 0))

    project_config = config_parser.parse_config()

    expected_license_configs = [
        SaulLicenseConfig(
            spdx_id="minimal",
            license_file=os.path.join(config_parser.project_dir, "MY.LICENSE"),
            copyright_year_start="1999",
            copyright_year_end="2002",
            copyright_holders="John 'foo' Doe",
            project_name="The Project",
            organization="Foobar Org.",
            homepage="foobar.project.org",
        )
    ]

    assert project_config.license_configs == expected_license_configs

    if save_config == "n":
        # The interactive session choice was to not save the config, so we expect no
        # config file in the project directory.
        assert not os.path.exists(
            os.path.join(config_parser.project_dir, config_parser.CONFIG_FILE_NAME)
        )
        # Similarly, re-running the config parser should prompt for a config.
        with pytest.raises(StopIteration):
            config_parser.parse_config()
    else:
        # The interactive session choice was to save the config, so we expect to find a
        # config file in the project directory.
        assert os.path.exists(
            os.path.join(config_parser.project_dir, config_parser.CONFIG_FILE_NAME)
        )
        # Re-running the config parser should not prompt for a config (it should parse
        # the config file automatically).
        project_config_2 = config_parser.parse_config()
        # The two configs should be identical.
        assert project_config == project_config_2


def test_interactive_config_default_values(
    monkeypatch: Any,
    config_parser: SaulConfigParser,
) -> None:
    """Test running an interactive config and accepting the default values."""
    # Provide input to the interactive configuration.
    interactive_input = iter(["minimal", "", "", "", "", "", "", "", ""])
    # "Hardcode" the year to 2023 so that the test is not impacted by the current year.
    monkeypatch.setattr(datetime, "datetime", datetime.datetime(2023, 1, 1, 0, 0, 0))
    monkeypatch.setattr("builtins.input", lambda _: next(interactive_input))

    project_config = config_parser.parse_config()

    expected_license_configs = [
        SaulLicenseConfig(
            spdx_id="minimal",
            license_file=os.path.join(
                config_parser.project_dir, config_parser.DEFAULT_LICENSE_FILE_NAME
            ),
            copyright_year_start="2023",
            copyright_year_end="2023",
            copyright_holders=None,
            project_name=None,
            organization=None,
            homepage=None,
        )
    ]

    assert project_config.license_configs == expected_license_configs


def test_interactive_config_unknown_license(
    monkeypatch: Any, config_parser: SaulConfigParser
) -> None:
    """Test running an interactive config and providing an unknown license."""
    # Provide input to the interactive configuration.
    interactive_input = iter(
        ["this_license_does_not_exist", "", "", "", "", "", "", "", "y"]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(interactive_input))

    with pytest.raises(
        UnknownLicenseError,
        match=re.escape(
            "<stdin>: Unknown license 'this_license_does_not_exist'. Run `saul list` "
            "to get a full list of available licenses."
        ),
    ):
        config_parser.parse_config()


@pytest.mark.parametrize(
    "inputs,missing_element",
    [
        pytest.param(
            ["needs_copyright_holders", "", "", "", "", "", "", "", ""],
            "copyright_holders",
            id="missing_copyright_holders",
        ),
        pytest.param(
            ["needs_project_name", "", "", "", "", "", "", "", ""],
            "project_name",
            id="missing_project_name",
        ),
        pytest.param(
            ["needs_organization", "", "", "", "", "", "", "", ""],
            "organization",
            id="missing_organization",
        ),
        pytest.param(
            ["needs_homepage", "", "", "", "", "", "", "", ""],
            "homepage",
            id="missing_homepage",
        ),
    ],
)
def test_interactive_config_missing_input_element(
    monkeypatch: Any,
    config_parser: SaulConfigParser,
    inputs: list[str],
    missing_element: str,
) -> None:
    """Test running an interactive config and not providing a required input element."""
    # Provide input to the interactive configuration.
    interactive_input = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(interactive_input))

    with pytest.raises(
        MissingInputElementError,
        match=re.escape(
            f"<stdin>: Missing license input element: '{missing_element}'."
        ),
    ):
        config_parser.parse_config()
