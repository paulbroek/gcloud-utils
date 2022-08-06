#!/usr/bin/env python

from setuptools import find_packages, setup

requires = []
setup(
    name="gcloud_utils",
    version="0.0.1",
    description="gcloud utils- \
        Google Cloud utilities, tips, tricks and helper functions to interact with BigQuery, Storage and more",
    url="git@github.com:paulbroek/gcloud-utils.git",
    author="Paul Broek",
    author_email="pcbroek@paulbroek.nl",
    license="unlicense",
    install_requires=requires,
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.8",
    zip_safe=False,
)
