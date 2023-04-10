import tempfile
from typing import Any, Generator

import pytest


@pytest.fixture()
def temp_dir(request: Any) -> Generator:
    """Provide a temporary directory to a test.

    This temporary directory can be used to avoid polluting the test directories.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
