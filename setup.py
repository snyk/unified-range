# from distutils.core import setup
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='unified_range',
    version='0.0.1-dev',
    packages=['unified_range', ],
    license='MIT License',
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
