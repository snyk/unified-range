# unified-range

Based on the VersionRange [model](https://github.com/apache/maven/tree/master/maven-artifact/src/main/java/org/apache/maven/artifact/versioning)
and [spec](https://maven.apache.org/enforcer/enforcer-rules/versionRanges.html) of maven.

Library to convert semver ranges to unified-range and the over way around.
Currently only supported for comparator semver ranges.

## Install
1. Use pipenv

`pipenv install unified-range`

or

2. Use pip directly

`pip install unified-range`

## How to use
1. Import the api module:

`from unified_range import api`

2. Convert from semver to the unified range (return VersionRange object):

`ver_rng = api.from_semver(semver_str)`

3. To get the string representation of a VersionRange object:

`version_range_str = str(ver_rng)`

3. Convert from unified spec to semver_str (return str):

`semver = api.to_semver(unified_spec_str)`

4. Convert from spec string to VersionRange objects:

`ver_rng = api.unified_range(unified_spec_str)`

5. Filter versions list by list of ranges:

`filtered_lst = api.filter_versions(ascending_version_list, ranges)`
The versions in `ascending_version_list` should be sorted in ascending order,
from oldest to newest, and contain all the versions for the package.

6. Filter next version and maximum versions from list of version and ranges:

`next_version = api.next_filtered_version(current_version, ascending_version_list, ranges)`
current_version must be part of the ascending_version_list list.

`max_versions = api.maximum_filtered_version(ascending_version_list, ranges)`


