import pytest
import os


@pytest.fixture()
def licenses_dir(request):
    # There should be a folder containing license files, with the same name as the
    # test itself, without the '.py' at the end.
    test_licenses_dir = request.module.__file__[:-3]
    assert os.path.isdir(
        test_licenses_dir
    ), f"Missing licenses dir for test {request.node.name}."

    yield test_licenses_dir
