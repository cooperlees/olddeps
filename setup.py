#!/usr/bin/env python3
# Copyright (c) 2014-present, Facebook, Inc.

from setuptools import setup
from sys import version_info


assert version_info >= (3, 7, 0), "od requires >= Python 3.7"
# TODO: Add tests :)
ptr_params = {
    "entry_point_module": "od",
    "test_suite": "od_tests",
    "test_suite_timeout": 300,
    "required_coverage": {"od.py": 69},
    "run_black": True,
    "run_mypy": True,
    "run_pyre": True,
}


setup(
    name="od",
    version="19.5.7",
    description=("Run a quick check to see how old modules are"),
    py_modules=["od"],
    python_requires=">=3.7",
    install_requires=["aiohttp", "click", "requirements-parser"],
    entry_points={"console_scripts": ["od = od:main"]},
    # test_suite=ptr_params[""]
)
