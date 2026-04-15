"""
pytest local configuration plug-in
"""

from __future__ import annotations

import os.path
import subprocess
import sys

import pytest


@pytest.fixture(scope="session")
def wheels_and_eggs(tmp_path_factory):
    """Build wheels and eggs from test distributions."""
    test_distributions = [
        "complex-dist",
        "simple.dist",
        "headers.dist",
        "commasinfilenames.dist",
        "unicode.dist",
    ]

    # PyPy on Windows cannot marshal-load .pyc files with non-ASCII module
    # names (setuptools' bdist_egg analyze_egg fails with
    # "bad marshal data (string is not ascii)"), so skip unicode.dist there.
    if sys.platform == "win32" and sys.implementation.name == "pypy":
        test_distributions.remove("unicode.dist")

    if sys.platform != "win32":
        # ABI3 extensions don't really work on Windows
        test_distributions.append("abi3extension.dist")

    pwd = os.path.abspath(os.curdir)
    this_dir = os.path.dirname(__file__)
    build_dir = tmp_path_factory.mktemp("build")
    dist_dir = tmp_path_factory.mktemp("dist")
    for dist in test_distributions:
        os.chdir(os.path.join(this_dir, "testdata", dist))
        subprocess.check_call(
            [
                sys.executable,
                "setup.py",
                "bdist_egg",
                "-b",
                str(build_dir),
                "-d",
                str(dist_dir),
                "bdist_wheel",
                "-b",
                str(build_dir),
                "-d",
                str(dist_dir),
            ]
        )

    os.chdir(pwd)
    return sorted(
        str(fname) for fname in dist_dir.iterdir() if fname.suffix in (".whl", ".egg")
    )


@pytest.fixture(scope="session")
def wheel_paths(wheels_and_eggs):
    return [fname for fname in wheels_and_eggs if fname.endswith(".whl")]


@pytest.fixture(scope="session")
def egg_paths(wheels_and_eggs):
    return [fname for fname in wheels_and_eggs if fname.endswith(".egg")]
