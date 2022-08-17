# saul

![CI](https://github.com/kokkonisd/saul/actions/workflows/ci.yaml/badge.svg)
![codecov](https://codecov.io/gh/kokkonisd/saul/branch/main/graph/badge.svg)

_You need a license for your project? 'saul good, man!_

Saul is a license generator based on [choosealicense.com](https://choosealicense.com).

## how to install

From PyPI:

```
$ pip install saul
```

From source:

```
$ python setup.py install
```

## how to use

First off, you can list the licenses that are available to you:

```
$ saul list
```

Once you've chosen a license, you can generate it by running:

```
$ saul generate <license>
```

For example, to generate the MIT license you can run:

```
$ saul generate mit
```

By default, this will trigger an interactive mode where you have to provide data if any
is needed for the license. For MIT for example, you need the year range and the
copyright holders:

```
$ saul generate mit
Year range? (example: 1999-2020)> 2022
Copyright holder(s)? (example: John Doe (doe@foo.com), Jane Doe (doe2@foo.com))> me
```

By default, your license will be placed in a `LICENSE` file at the current directory.
You can change that by providing the path to an output file via the `-o/--output`
option. You can also choose to just dump the generated license text in stdout by using
the `-n/--no-file` option.

If you know what information is needed by the license, you can also provide it via CLI
options. For example, the one-liner to generate the exact same MIT license as the
previous example is:

```
$ saul generate mit -y 2022 -c me
```
