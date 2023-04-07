import os

import pytest


@pytest.fixture()
def licenses_dir(request):
    """Get the licenses directory.

    For a given test, there should be a corresponding directory containing license
    files.
    """
    # There should be a directory containing license files, with the same name as the
    # test itself, without the '.py' at the end.
    test_licenses_dir = request.module.__file__[:-3]
    assert os.path.isdir(
        test_licenses_dir
    ), f"Missing licenses dir for test {request.node.name}."

    yield test_licenses_dir
