from unified_range import utils
from unified_range import models


def from_semver(semver_spec):
    """
    Convert semver string to unified range string.
    :param semver_spec: str
    :return: unified_spec
    """
    ver_rng = utils.create_from_semver(semver_spec)
    return str(ver_rng)


def to_semver(spec):
    """
    Convert unified range string to semver string.
    :param spec: str
    :return: semver
    """
    semver = utils.transform_to_semver(spec)
    return semver


def unified_range(spec):
    """
    Return VersionRange for unified range.
    Only support unified range format.
    :param spec: str
    :return: VersionRange instance
    """
    return models.UnifiedVersionRange.create_from_spec(spec)
