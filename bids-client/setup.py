# coding: utf-8

"""
    Flywheel Bids Client
"""
import os
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install

NAME = "flywheel-bids"
VERSION = "0.7.1"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["jsonschema>=2.6.0", "flywheel-sdk>=2.4.0", "future>=0.16.0"]

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'Verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')
        if tag != VERSION:
            sys.exit('Git tag: {0} does not match version: {1}'.format(tag, VERSION))

setup(
    name=NAME,
    version=VERSION,
    description="Flywheel BIDS Client",
    author_email="support@flywheel.io",
    url="",
    keywords=["Flywheel", "flywheel", "BIDS", "SDK"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'flywheel_bids': ['templates/*.json']
    },
    license="MIT",
    project_urls={
        'Source': 'https://github.com/flywheel-io/bids-client'
    },
    entry_points = {
        'console_scripts': [
            'curate_bids=flywheel_bids.curate_bids:main',
            'export_bids=flywheel_bids.export_bids:main',
            'upload_bids=flywheel_bids.upload_bids:main'
        ]
    },
    cmdclass = {
        'verify': VerifyVersionCommand
    },
    long_description=
'''
Flywheel BIDS Client
============

An SDK for interacting with BIDS formatted data on a Flywheel instance.
'''
)
