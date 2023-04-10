import os
import tempfile

from saul import LICENSES_DIR
from saul.license.parser import LicenseParser

# We can ignore the I900 error here, this is purely to make mypy happy.
from tests.cli.conftest import SaulCLI  # noqa: I900


def test_cli_without_arguments(saul_cli: SaulCLI) -> None:
    """Test running `saul` without any arguments."""
    res = saul_cli.run()
    assert res.returncode == 0

    # Should print the help screen.
    assert "usage: saul" in res.stdout


def test_cli_list(saul_cli: SaulCLI) -> None:
    """Test running `saul list`."""
    res = saul_cli.run("list")
    assert res.returncode == 0

    # Should print the list of available licenses.
    license_parser = LicenseParser(LICENSES_DIR)
    known_licenses = license_parser.parse_license_templates()

    for _license in known_licenses:
        assert _license.spdx_id.lower() in res.stdout


def test_cli_generate(saul_cli: SaulCLI) -> None:
    """Test running `saul generate`."""
    with tempfile.TemporaryDirectory() as project_dir:
        with open(os.path.join(project_dir, ".saul"), "w") as config_file:
            config_file.write(
                "\n".join(
                    [
                        "[[licenses]]",
                        'license = "mit"',
                        'file = "LICENSE"',
                        'copyright_holders = "Test Person"',
                        'copyright_year_start = "2003"',
                    ]
                )
            )

        res = saul_cli.run("generate", cwd=project_dir)
        assert res.returncode == 0

        # Check that a license file was indeed generated.
        assert os.path.isfile(os.path.join(project_dir, "LICENSE"))

        # Check that the license file contains the right information.
        with open(os.path.join(project_dir, "LICENSE"), "r") as license_file:
            license_contents = license_file.read()

        assert "Test Person" in license_contents
        assert "2003" in license_contents
