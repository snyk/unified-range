# unified-range

Library to convert semver to unified-range and the over way around.

## Install
1. Use pipenv (`pipenv install unified-range`)
or 
2. `pip install unified-range`

## How to use
1. Import the api module:
`from unified_range import api`
2. Convert from semver to the unified range (return VersionRange object):
`v = api.from_semver(semver_str)`
3. To get the string representation of a VersionRange object:
`version_range_str = str(v)`
3. Convert from unified spec to semver_str (return str):
`semver = api.to_semver(unified_spec_string)`

