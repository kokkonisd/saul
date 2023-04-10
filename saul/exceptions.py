"""The exceptions module.

This module contains definitions for the different exceptions that can be raised by
saul.
"""


class SaulError(Exception):
    """Implement the SaulError exception.

    This is the base/catchall exception on which all other exceptions are built.
    """


class SaulConfigError(SaulError):
    """Implement the SaulConfigError exception.

    This exception signifies an issue with the project- or license-level configuration.
    """


class LicenseParserError(SaulError):
    """Implement the LicenseParserError exception.

    This exception signifies an issue with the parsing of the license template files.
    """


class LicenseGeneratorError(SaulError):
    """Implement the LicenseGeneratorError exception.

    This exception signifies an issue with the generation of license files.
    """


class UnknownLicenseError(SaulError):
    """Implement the UnknownLicenseError exception.

    This exception signifies that the license the user asked for is not known.
    """


class MissingInputElementError(SaulError):
    """Implement the MissingInputElementError exception.

    This exception signifies that a license input element (e.g. copyright holder names)
    is missing, and thus the license cannot be generated.
    """
