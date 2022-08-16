#!/bin/usr/env python

import argparse
import pkg_resources
import sys

from saul.license import LicenseGenerator, LicenseInputElement

LICENSES_DIR = pkg_resources.resource_filename(__name__, "licenses")


def list_cmd(args: argparse.Namespace) -> None:
    known_licenses = args.license_generator.known_licenses
    max_id_length = max([len(spdx_id) for spdx_id in known_licenses.keys()])

    print(
        "\n".join(
            sorted(
                [
                    f"{spdx_id:{max_id_length}}: {license['full_name']}"
                    for spdx_id, license in known_licenses.items()
                ]
            )
        )
    )


def generate_cmd(args: argparse.Namespace) -> None:
    # If any license input elements are supplied, do not run in interactive mode (the
    # user probably wants to avoid that by supplying them directly as arguments).
    interactive = not any(
        [
            getattr(args, element) is not None
            for element in [e.value.lower() for e in LicenseInputElement]
        ]
    )

    license_body, license_note = args.license_generator.generate_license(
        license_id=args.license,
        interactive=interactive,
        year_range=args.year_range,
        copyright_holders=args.copyright_holders,
        organization=args.organization,
        project_name=args.project_name,
        homepage=args.homepage,
        from_cli=True,
    )

    if args.no_file:
        print(license_body, end="")
    else:
        license_filepath = args.output or args.license_generator.DEFAULT_FILENAME
        with open(license_filepath, "w") as license_file:
            license_file.write(license_body)

    if license_note is not None:
        print(f"\033[2;33mNote: {license_note}\033[0m", file=sys.stderr)


def main() -> None:
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
    generate_subparser.add_argument("license")
    generate_subparser.add_argument(
        "-y",
        "--year-range",
        help=(
            "The year range of the validity of the license, or just the current year. "
            "Examples: '1999-2020', '2022'."
        ),
    )
    generate_subparser.add_argument(
        "-c",
        "--copyright-holders",
        help=(
            "The copyright holders and their emails, separated with commas. Example: "
            "'John Doe (doe@foo.com), Jane Doe (doe2@foo.com)'."
        ),
    )
    generate_subparser.add_argument(
        "-g",
        "--organization",
        help="The name of the group or organization backing the project.",
    )
    generate_subparser.add_argument(
        "-p", "--project-name", help="The name of the project."
    )
    generate_subparser.add_argument(
        "-w", "--homepage", help="The homepage/website of the project."
    )

    output_options_group = generate_subparser.add_mutually_exclusive_group()
    output_options_group.add_argument(
        "-o",
        "--output",
        help=(
            "The file to output the license to (otherwise a default will be chosen, "
            "usually LICENSE)."
        ),
    )
    output_options_group.add_argument(
        "-n",
        "--no-file",
        help="Do not write the license to a file; output to stdout instead.",
        action="store_true",
    )

    generate_subparser.set_defaults(func=generate_cmd)

    license_generator = LicenseGenerator(licenses_dir=LICENSES_DIR)
    parser.set_defaults(func=None, license_generator=license_generator)

    args = parser.parse_args()
    assert args is not None

    if args.func is not None:
        args.func(args)
    else:
        parser.print_help()
