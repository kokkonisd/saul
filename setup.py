#!/usr/bin/env python

import setuptools

from saul import name, description, __version__, __author_name__, __author_email__

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name=name,
    version=__version__,
    author=__author_name__,
    author_email=__author_email__,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kokkonisd/saul",
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=["tomlkit"],
    packages=["saul"],
    include_package_data=True,
    package_data={"saul": ["licenses/*.toml"]},
    entry_points={"console_scripts": ["saul = saul.__main__:main"]},
    python_requires=">=3.9",
)
