#!/usr/bin/env python

from setuptools import setup

setup(
    name='replay',
    version='1.0',
    description='Access log player',
    author='Pavel Patrin',
    author_email='pavelpatrin@gmail.com',
    url='https://github.com/pavelpatrin/replay',
    packages=['replay'],
    install_requires=[
        'argparse',
        'requests',
    ],
)
