import os
import shutil
import tempfile
from typing import Any, Generator

import pytest


@pytest.fixture()
def test_data_dir(request: Any) -> Generator:
    """Provide the test data directory associated with a given test.

    This fixture assumes that a directory with the same name as the test exists; that
    directory is used as the test data directory, containing various data pertaining to
    the test.
    """
    # The test data directory has the same name as the test, minus the `.py` at the end.
    licenses_dir = request.module.__file__[:-3]
    assert os.path.isdir(
        licenses_dir
    ), f"Missing test data dir for test {request.node.name}."

    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copytree(licenses_dir, temp_dir, dirs_exist_ok=True)

        yield temp_dir
