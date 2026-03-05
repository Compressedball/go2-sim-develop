from setuptools import find_packages
from setuptools import setup

setup(
    name='new_interface',
    version='0.0.0',
    packages=find_packages(
        include=('new_interface', 'new_interface.*')),
)
