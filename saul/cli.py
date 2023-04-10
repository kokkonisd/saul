"""The entrypoint to saul's CLI."""

import argparse

from saul import LICENSES_DIR
from saul.config.parser import SaulConfigParser
from saul.license.generator import LicenseGenerator
from saul.license.parser import LicenseParser


def list_cmd(args: argparse.Namespace) -> None:
    """Run the `list` command.

    :param args: arguments to the command.
    """
    max_id_length = max([len(_license.spdx_id) for _license in args.known_licenses])

    print(
        "\n".join(
            sorted(
                [
                    f"{_license.spdx_id.lower():{max_id_length}}: {_license.full_name}"
                    for _license in args.known_licenses
                ]
            )
        )
    )


def generate_cmd(args: argparse.Namespace) -> None:
    """Run the `generate` command.

    :param args: arguments to the command.
    """
    config_parser = SaulConfigParser(
        project_dir=".", known_licenses=args.known_licenses
    )
    project_config = config_parser.parse_config()
    generator = LicenseGenerator(known_licenses=args.known_licenses)
    generator.generate_licenses(project_config)


def main() -> None:
    """Run the main entry point for saul's CLI."""
    parser = argparse.ArgumentParser(description="Generate licenses for your projects.")

    subparsers = parser.add_subparsers()

    list_subparser = subparsers.add_parser("list", help="List all known licenses.")
    list_subparser.set_defaults(func=list_cmd)

    generate_subparser = subparsers.add_parser(
        "generate",
        help=(
            "Generate a license file. Run `saul list` to get a list of known licenses."
        ),
    )

    output_options_group = generate_subparser.add_mutually_exclusive_group()
    output_options_group.add_argument(
        "-n",
        "--no-file",
        help="Do not write the license to a file; output to stdout instead.",
        action="store_true",
    )

    generate_subparser.set_defaults(func=generate_cmd)

    license_parser = LicenseParser(LICENSES_DIR)
    parser.set_defaults(func=None)

    args = parser.parse_args()
    assert args is not None

    if args.func is not None:
        args.known_licenses = license_parser.parse_license_templates()
        args.func(args)
    else:
        parser.print_help()
