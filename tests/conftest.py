import os
import subprocess

import pytest

LICENSES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, "saul", "license_templates"
)

assert os.path.isdir(LICENSES_DIR), LICENSES_DIR


class SaulCLI:
    """Dummy object implementing a call to the CLI of saul."""

    def run(self, *args, _input=None, cwd=".") -> subprocess.CompletedProcess:
        """Run saul in CLI mode with optional arguments.

        :param input: input to feed to the process.
        :return: the result of the process running saul.
        """
        return subprocess.run(
            ["saul", *args],
            capture_output=True,
            text=True,
            input=_input,
            cwd=cwd,
        )


@pytest.fixture()
def saul_cli():
    """Generate a SaulCLI instance."""
    yield SaulCLI()


@pytest.fixture()
def license_files():
    """Get the list of license files."""
    yield os.listdir(LICENSES_DIR)
