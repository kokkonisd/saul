import pytest
import subprocess
import os


LICENSES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, "saul", "licenses"
)

assert os.path.isdir(LICENSES_DIR), LICENSES_DIR


class SaulCLI:
    """Dummy object implementing a call to the CLI of saul."""

    def run(self, *args, input=None, cwd=".") -> subprocess.CompletedProcess:
        """Run saul in CLI mode with optional arguments.

        :param input: input to feed to the process.
        :return: the result of the process running saul.
        """
        return subprocess.run(
            ["saul", *args],
            capture_output=True,
            text=True,
            input=input,
            cwd=cwd,
        )


@pytest.fixture()
def saul_cli():
    yield SaulCLI()


@pytest.fixture()
def license_files():
    yield os.listdir(LICENSES_DIR)
