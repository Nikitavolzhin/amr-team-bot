from setuptools import find_packages
from setuptools import setup

setup(
    name='robile_navigation',
    version='0.0.0',
    packages=find_packages(
        include=('robile_navigation', 'robile_navigation.*')),
)
