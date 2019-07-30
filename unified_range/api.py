from typing import List

from unified_range import utils

from unified_range.models import UnifiedVersionRange
from unified_range.utils import is_semver_range, is_unified_range


def from_semver(semver_spec: str) -> str:
    """
    Convert semver string to unified range string.
    :param semver_spec: str
    :return: unified_spec
    """
    ver_rng = utils.create_from_semver(semver_spec)
    return str(ver_rng)


def to_semver(spec: str) -> str:
    """
    Convert unified range string to semver string.
    :param spec: str
    :return: semver
    """
    semver = utils.transform_to_semver(spec)
    return semver


def unified_range(spec: str) -> UnifiedVersionRange:
    """
    Return VersionRange for unified range.
    Only support unified range format.
    :param spec: str
    :return: VersionRange instance
    """
    return UnifiedVersionRange.create_from_spec(spec)


def filter_versions(asc_versions: List[str], ranges: List[str]) -> List[str]:
    """
    Return an ordered list of versions that not satisfies any range.
    Input versions must be ordered in ascending order and include all
    the versions that are specified in the ranges.
    :param ord_versions:
    :param ranges:
    :return:
    """
    rngs_unified = []
    for rng in ranges:
        if is_semver_range(rng):
            rngs_unified.append(unified_range(from_semver(rng)))
        elif is_unified_range(rng):
            rngs_unified.append(unified_range(rng))
        else:
            raise ValueError(
                f'Not a valid semver or unified/maven range - ({rng})')

    return utils.not_included_versions(asc_versions, rngs_unified)


def next_filtered_version(current_version: str, asc_versions: List[str],
                          ranges: List[str]) -> List[str]:
    """
    Return the first version that not satisfies any range.
    Input versions must be ordered in ascending order and include all
    the versions that are specified in the ranges.
    """
    if current_version not in asc_versions:
        raise ValueError('current_version given is not part of asc_version')
    minimal_version = None
    index_current_version = asc_versions.index(current_version)
    filtered_versions = filter_versions(asc_versions, ranges)
    for v in filtered_versions:
        if index_current_version <= asc_versions.index(v):
            minimal_version = v
            break
    return minimal_version


def maximum_filtered_version(asc_versions: List[str],
                             ranges: List[str]) -> List[str]:
    """
    Return the first version that not satisfies any range.
    Input versions must be ordered in ascending order and include all
    the versions that are specified in the ranges.
    """
    filtered_versions = filter_versions(asc_versions, ranges)
    if filtered_versions:
        return filtered_versions[-1]
    else:
        return None
