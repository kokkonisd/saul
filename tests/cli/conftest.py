import os
import subprocess
from typing import Generator

import pytest

from saul import LICENSES_DIR

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
def saul_cli() -> Generator:
    """Generate a SaulCLI instance."""
    yield SaulCLI()


@pytest.fixture()
def license_files() -> Generator:
    """Get the list of license files."""
    yield os.listdir(LICENSES_DIR)
