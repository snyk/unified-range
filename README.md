# unified-range

The library converts input semver ranges to a uniform model, and the other way around, providing objects that are easier to use programmatically.

## Examples of supported ranges
1. npm style semver - `<1.2.3 >=2.0.0`
2. ruby style semver - `<1.2.3, >=2.0.0`
3. maven style version ranges - `[1.2.3,2.1.1), [3.0.0,4.1.1)`


Additionally, use this library to run algorithms on any input version ranges and calculate whether a specific version is included in this range.


## Prerequisites

1. Ensure you have installed either pip or pipenv
2. Install:
   `pipenv install unified-range` or `pip install unified-range`

3. Import the `api` module:
   `from unified_range import api`

## How to use
Following are the different functions you can perform with this library.


### To convert a range to the uniform string range, from the semver format:

`ver_rng = api.from_semver(semver_str)`

Results: uniform range structure

### Convert from the uniform range structure to a semver string (return str):

`semver = api.to_semver(unified_spec_str)`


### To convert the versionrange object to a string:

`version_range_str = str(ver_rng)`


### Convert from the uniform string to the uniform model object (VersionRange objects):

`ver_rng = api.unified_range(unified_spec_str)`

```
>>> api.unified_range('[1.2.3,4.5.6)')
<unified_range.models.UnifiedVersionRange at 0x7f7e4dc17320>
```

### Within a list of ranges, retrieve versions not included:

`filtered_lst = api.filter_versions(ascending_version_list, ranges)`
```
>>> api.filter_versions(['0.1', '0.2', '1.0', '1.1', '2.0'], ['[,0.2]', '[1.1]'])
['1.0', '2.0']
```


The versions in `ascending_version_list` should be sorted in ascending order,
from oldest to newest, and contain all the versions for the package.


### From a list of version ranges, retrieve the closest version in the list to the current version (next):
Filter next version and maximum version from list of version and ranges:

`next_version = api.next_filtered_version(current_version, ascending_version_list, ranges)`
current_version must be included in the ascending_version_list.
```
>>> api.next_filtered_version(current_version='0.2', ascending_version_list=['0.1', '0.2', '1.0', '1.1', '2.0'], ranges=['[,0.2]', '[1.1]'])
'1.0'

>>> api.next_filtered_version(current_version='1.1', ascending_version_list=['0.1', '0.2', '1.0', '1.1', '2.0'], ranges=['[,0.2]', '[1.1]'])
'2.0'
 ```

### Retreive the latest version that is not included:
`max_version = api.maximum_filtered_version(ascending_version_list, ranges)`
```
>>> api.maximum_filtered_version(ascending_version_list=['0.1', '0.2', '1.0', '1.1', '2.0'], ranges=['[,0.2]', '[1.1]'])
'2.0'
 ```

## Uniform structure examples

Following are the uniform structures used in this library:

Uniform string structure example: (,1.2.3)

### Uniform model examples:

`UnifiedVersionRange.constraints -> List[Restrictions]`

`Restriction.bounds -> Tuple[Bound, Bound]`

`Bound.version -> str`

`Bound.inclusive -> boolean`


## References and prior works

This library was built with the following:
1. Maven’s VersionRange:
[model](https://github.com/apache/maven/tree/master/maven-artifact/src/main/java/org/apache/maven/artifact/versioning) and [spec](https://maven.apache.org/enforcer/enforcer-rules/versionRanges.html) of maven.
2. https://semver.org/
3. [npm’s semver library](https://www.npmjs.com/package/semver )
