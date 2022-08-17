import nox


TEST_DEPS = [
    ("pytest", "7.1.2"),
    ("pytest-cov", "3.0.0"),
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
    session.run("pytest", "-vv", "--cov=saul")


@nox.session(python=MAIN_PYTHON_VERSION)
def lint(session: nox.Session) -> None:
    # Install the developer requirements.
    session.install("-r", "dev_requirements.txt")
    # Run pre-commit.
    session.run("pre-commit", "run", "--all-files")
