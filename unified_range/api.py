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


def inter(versions: List[str], rngs: List[str]):
    rngs_unified = []
    for rng in rngs:
        if is_semver_range(rng):
            rngs_unified.append(unified_range(from_semver(rng)))
        elif is_unified_range(rng):
            rngs_unified.append(unified_range(rng))
        else:
            raise ValueError(
                f'Not a valid semver or unified/maven range - ({rng})')

    return utils.not_inculded_versions(versions, rngs_unified)
