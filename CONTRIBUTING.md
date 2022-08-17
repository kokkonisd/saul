# how to contribute

Saul is an open source project and everyone is welcome to contribute :)

Please open an issue and discuss with the maintainers before going ahead and opening a
PR.


## getting started

First off, clone this repo, then set up your development environment (Python >= 3.9
required):

```
$ python -m venv saul_venv/
$ source saul_venv/bin/activate
$ python -m pip install -r dev_requirements.txt
$ nox
```

The `nox` command should complete successfully and exit with a code 0. If not, your
environment is not set up properly.

If everything is okay, you can start working on your contribution!


## adding a license

### bare minimum

The license files are written in TOML, and are situated under `saul/licenses/`. They
must contain some basic key-value pairs (specifically the keys mentioned in
`saul.license.LicenseGenerator.MANDATORY_LICENSE_KEYS`). You can see how those are used
by looking at the other licenses.

A basic, minimal license will look something like this:

```toml
full_name = "Official License Name"
spdx_id = "Official-SPDX-ID"

body = '''
Lorem ipsum...
'''
```


### license requiring input/modification

If the license requires the user to fill in some data (like the year range covered by
the license, or the names of the copyright holders), you should add these in a 'replace'
key (see `saul/licenses/mit.toml` for an example of this).

Again, simple example:

```toml
full_name = "Official License Name"
spdx_id = "Official-SPDX-ID"
replace = [
    { string = "<year>", element = "YEAR_RANGE" },
    { string = "<name>", element = "COPYRIGHT_HOLDERS" }
]

body = '''
Copyright (c) <year> <name>

Lorem ipsum...
'''
```

The input elements (`"YEAR_RANGE"`, `"COPYRIGHT_HOLDERS"`, ...) that are considered to
be valid are listed in the `saul.license.LicenseInputElement` enum. If the license
you're adding needs an additional input element not currently present on the enum, feel
free to add it.


### license notes

If any notes are needed (meaning any extra information that needs to be passed to the
user, like where they should put the license file or what they should call it), you
should add them under the 'notes' key (see `saul/licenses/gpl-3.0.toml` for an example
of this).

Simple example of a note:

```toml
full_name = "Official License Name"
spdx_id = "Official-SPDX-ID"

note = """\
This license should always be placed in the directory containing the source code.\
"""

body = '''
Lorem ipsum...
'''
```


## style guide

Please try to respect the style guide established by the existing TOML license files.
