# Contributing (WIP)

This document details the contribution guidelines and procedures for pyCascadia.

## Uploading to PyPi

Uploading the latest version of `pyCascadia` to PyPi is currently done manually via the following steps. This must be done by an employee of UCL's research software development group.

1. Create the package:

```
python setup.py sdist bdist_wheel
```

2. Check with `twine`:

```
twine check dist/*
```

3. If twine reports no errors or warnings, upload to PyPi (optionally uploading to testpypi first)

```
python3 -m twine upload [--repository testpypi] dist/*
```
