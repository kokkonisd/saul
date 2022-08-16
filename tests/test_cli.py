import os
import tempfile


def test_cli_no_args(saul_cli):
    """Test a call with no arguments."""
    res = saul_cli.run()
    # Should print the help screen.
    assert res.returncode == 0


def test_cli_list(saul_cli, license_files):
    """Test the call to the 'list' subcommand."""
    res = saul_cli.run("list")

    assert res.returncode == 0
    # Should print the complete list of licenses.
    for license_file in license_files:
        spdx_id = os.path.split(license_file)[-1][:-5]
        assert (
            spdx_id in res.stdout
        ), f"License {spdx_id} not found in the output of `saul list`."

    # Only valid licenses should be in that output.
    assert "this-is-absolutely-not-a-real-license-3.0" not in res.stdout

    # Nothing should be printed in stderr.
    assert res.stderr == ""


def test_cli_generate_no_args(saul_cli):
    """Test the call to the 'generate' subcommand."""
    res = saul_cli.run("generate")
    # Should expect a license name to generate.
    assert res.returncode == 2
    assert "the following arguments are required: license" in res.stderr


def test_cli_generate_no_input(saul_cli):
    """Test the generation of a license that requires no input."""
    res = saul_cli.run("generate", "gpl-3.0", "-n")
    # Should generate a license.
    assert res.returncode == 0
    assert "GNU GENERAL PUBLIC LICENSE" in res.stdout


def test_cli_generate_with_input(saul_cli):
    """Test the generation of a license that requires some input."""
    # Feed the input through stdin.
    repl_res = saul_cli.run(
        "generate", "mit", "-n", input="1980-2022\nJohn Doeman (doeman@corp.com)\n"
    )
    assert "MIT License" in repl_res.stdout
    assert "Copyright (c) 1980-2022 John Doeman (doeman@corp.com)" in repl_res.stdout

    # Now feed the input through CLI switches.
    switch_res = saul_cli.run(
        "generate",
        "mit",
        "-n",
        "-y",
        "1980-2022",
        "-c",
        "John Doeman (doeman@corp.com)",
    )
    assert "MIT License" in switch_res.stdout
    assert "Copyright (c) 1980-2022 John Doeman (doeman@corp.com)" in switch_res.stdout

    # The two licenses should be the same except for the input prompts in the REPL one.
    assert repl_res.stdout.split(")> ")[-1] == switch_res.stdout


def test_cli_generate_partial_input(saul_cli):
    """Test the generation of a license with part of the input missing."""
    # MIT requires both year range and copyright holders, so this should throw an error.
    res = saul_cli.run(
        "generate",
        "mit",
        "-n",
        "-y",
        "1980-2022",
    )

    assert res.returncode == 1
    assert "'--copyright-holders' is required for the MIT license." in res.stderr


def test_cli_generate_license_file(saul_cli):
    """Test the generation of an actual license file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate a custom COPYING license file.
        license_filepath = os.path.join(temp_dir, "COPYING")
        assert not os.path.isfile(license_filepath)

        res = saul_cli.run("generate", "gpl-2.0", "-o", license_filepath)
        assert res.returncode == 0
        assert os.path.isfile(license_filepath)

        with open(license_filepath, "r") as license_file:
            license_text = license_file.read()
        assert license_text
        assert "GNU GENERAL PUBLIC LICENSE" in license_text

        # Generate a default license file.
        license_filepath = os.path.join(temp_dir, "LICENSE")
        assert not os.path.isfile(license_filepath)

        res = saul_cli.run("generate", "gpl-2.0", cwd=temp_dir)
        assert res.returncode == 0
        assert os.path.isfile(license_filepath)

        with open(license_filepath, "r") as license_file:
            license_text = license_file.read()
        assert license_text
        assert "GNU GENERAL PUBLIC LICENSE" in license_text
