from setuptools import find_packages
from setuptools import setup

setup(
    name='robile_interfaces',
    version='0.0.0',
    packages=find_packages(
        include=('robile_interfaces', 'robile_interfaces.*')),
)
