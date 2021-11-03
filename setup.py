# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

def read(rel_path):
    """Read lines from given file"""
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    """Read __version__ from given file"""
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError(f'Unable to find a valid __version__ string in {rel_path}.')


requirements = [
    'tqdm>=4.49.0',
    'pandas>=1.0.0',
    'numpy>=1.21.3',
    'loguru>=0.5.3',
    'document-utils>=1.3.0',
    'requests>=2.0.0'
]

test_requirements = [
            'pytest',
            'pytest-dotenv',
            'pytest-cov',
            'openpyxl==3.0.9',
            'fsspec==2021.10.1',
        ]

dev_requirements = [
    'autopep8',
    'flake8',
    'pylint',
    'pre-commit',
    'cython>=0.29.24'
]+test_requirements


setup(
    name='VecDB',
    version=get_version('vecdb/__init__.py'),
    url='',
    author='Relevance AI',
    author_email='dev@vctr.ai',
    long_description='',

    package_dir={'': 'vecdb'},
    packages=find_packages(where='vecdb'),
    setup_requires=['wheel'],
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
        'tests': test_requirements,
        'excel': [
            'fsspec==2021.10.1',
            'openpyxl==3.0.9'
        ]
    },
    python_requires='>=3.7',
    classifiers=[],
)
