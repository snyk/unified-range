# from distutils.core import setup
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='unified_range',
    description="Convert between semver range and maven version range",
    url="https://github.com/snyk/unified-range",
    version='0.0.4',
    packages=['unified_range', ],
    license='MIT License',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
