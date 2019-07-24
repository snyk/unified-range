# from distutils.core import setup
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='unified_range',
    description="Convert between semver range and maven version range",
    url="https://github.com/snyk/unified-range",
    version='0.0.9',
    # packages=['unified_range', ],
    packages=find_packages(),
    license='MIT License',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'attrs',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
