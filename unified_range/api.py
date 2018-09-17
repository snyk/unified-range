from unified_range import utils
from unified_range import models


def from_semver(semver_spec):
    ver_rng = utils.create_from_semver(semver_spec)
    return ver_rng


def to_semver(spec):
    semver = utils.transform_to_semver(spec)
    return semver


# fixme: REMOVE!
def unified_version(spec):
    v = models.UnifiedVersionRange.create_from_spec(spec)
    return v