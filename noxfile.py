import nox


TEST_DEPS = [
    ("pytest", "7.1.2"),
    ("pytest-cov", "3.0.0"),
]

STYLE_CHECK_DEPS = [
    ("flake8", "5.0.4"),
    ("mypy", "0.971"),
    ("black", "22.6.0"),
    ("types-setuptools", "64.0.1"),
]

MAIN_PYTHON_VERSION = "3.9"
SUPPORTED_PYTHON_VERSIONS = [MAIN_PYTHON_VERSION, "3.10"]


@nox.session(python=SUPPORTED_PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the testsuite."""
    # Install the runtime requirements.
    session.install("-r", "requirements.txt")
    # Install the test dependencies.
    for dep, version in TEST_DEPS:
        session.install(f"{dep}=={version}")
    # Install saul itself.
    session.install("-e", ".")

    # Run the testsuite & coverage report.
    session.run("pytest", "-vv", "--cov=saul", "--cov-report=term")


@nox.session(python=MAIN_PYTHON_VERSION)
def style_checks(session: nox.Session) -> None:
    """Run the style checks."""
    # Install the runtime requirements.
    session.install("-r", "requirements.txt")
    # Install the style check dependencies and the test dependencies.
    for dep, version in STYLE_CHECK_DEPS + TEST_DEPS:
        session.install(f"{dep}=={version}")

    # Run the style checks.
    session.run("flake8")
    session.run("mypy", "saul/", "tests/")
    session.run("black", "saul/", "tests/")
