import re
from typing import List, Optional

from unified_range import models

from unified_range.models import UnifiedVersionRange

semver_operators = {"lt": "<", "lte": "<=", "gt": ">", "gte": ">=", "eq": "="}
unified_operators = {"lt": ")", "lte": "]", "gt": "(", "gte": "["}


def _is_unified_ops(rng):
    return any(op in rng for op in unified_operators.values())


def _is_semver_ops(rng):
    return any(op in rng for op in semver_operators.values())


def _clean_semver(semver):
    # also cleaning `v=X.X.X` `= X.X.X`
    # TODO: regex catching invalid semvers `<=v1.2.3` => `<1.2.3'
    remove_eq = re.sub(r'(?<![<>])=?v?(?=.*?)', '', semver.strip())
    remove_eq_v = re.sub(r'(?<=[<>])v?(?=.*?)', '', remove_eq)
    return remove_eq_v


def _comparator_trim(semver: str) -> str:
    """
    clean spaces between operator to the version.
    `> 1.2.3 <= 1.2.5` => `>1.2.3 <=1.2.5`
    :param semver:
    :return:
    """
    # switch `,` to ` ` for composer versions
    if ',' in semver:
        semver = semver.replace(',', ' ')
    COMPARTOR_TRIM = r'\s+(?=[^<>|])'
    return re.sub(COMPARTOR_TRIM, '', semver.strip())


def is_semver_range(rng):
    return _is_semver_ops(rng) and not _is_unified_ops(rng)


def is_unified_range(rng):
    return _is_unified_ops(rng) and not _is_semver_ops(rng)


def transform_to_semver(unified_spec: str) -> str:
    """
    Transform unified spec (following the maven VersioRange spec,
    https://maven.apache.org/enforcer/enforcer-rules/versionRanges.html)
    to semver range string representation (following npm/node spec,
    https://github.com/npm/node-semver#ranges).

    (1.2.3, 2.4.6] ----> >1.2.3 <=2.4.6
    :param unified_spec: str
    :return: semver: string
    """
    # FIXME: use semver_operators and _is_semver_{ops,range}
    operators = {"lt": "<", "lte": "<=", "gt": ">", "gte": ">="}

    if is_semver_range(unified_spec):
        raise ValueError(
            "Version ranges seems to already be semver")
    contains_all_version = models.UnifiedVersionRange(None, [
        models.Restriction.all_versions()])
    unified_version = models.UnifiedVersionRange.create_from_spec(unified_spec)
    if unified_version == contains_all_version:
        return "*"

    unified_restrictions = unified_version.restrictions
    semvers = []

    for restriction in unified_restrictions:
        if restriction.upper_bound.version and restriction.lower_bound.version:
            # specific version
            if restriction.lower_bound.version == restriction.upper_bound.version:
                semvers.append("{}".format(restriction.upper_bound))
            # two constraints semver `>1.1.2 <=2.0.0`
            # `{operator}{version} {operator}{version}`
            else:
                gt_gte = operators["gt"]
                if restriction.has_inclusive_lower:
                    gt_gte = operators["gte"]
                lt_lte = operators["lt"]
                if restriction.has_inclusive_upper:
                    lt_lte = operators["lte"]
                semvers.append(
                    "{}{} {}{}".format(gt_gte, restriction.lower_bound,
                                       lt_lte, restriction.upper_bound))
        # one constraint semver `>=1.2.3`
        # {operator}{version}
        else:
            if restriction.upper_bound.version and not restriction.lower_bound.version:
                lt_lte = operators["lt"]
                if restriction.has_inclusive_upper:
                    lt_lte = operators["lte"]
                semvers.append(
                    "{}{}".format(lt_lte, restriction.upper_bound))
            elif restriction.lower_bound.version and not restriction.upper_bound.version:
                gt_gte = operators["gt"]
                if restriction.has_inclusive_lower:
                    gt_gte = operators["gte"]
                semvers.append(
                    "{}{}".format(gt_gte, restriction.lower_bound))
            else:
                raise ValueError("lower and upper bound are None")
    return " || ".join(semvers)


def create_from_semver(semver: str) -> UnifiedVersionRange:
    """
    Transform semver range string (following npm/node spec,
    https://github.com/npm/node-semver#ranges).

    to unified VersionRange (following the maven VersioRange spec,
    https://maven.apache.org/enforcer/enforcer-rules/versionRanges.html).

    >1.2.3 <=2.4.6 ----> (1.2.3, 2.4.6]
    :param semver: str
    :return: VersionRange
    """
    operators = {"lt": "<", "lte": "<=", "gt": ">", "gte": ">="}

    if is_unified_range(semver):
        raise ValueError(
            "Version ranges seems to already be maven version range")
    if not any(op in semver for op in operators.values()):
        semver = _clean_semver(semver)
    else:
        semver = _comparator_trim(semver)

    if semver == "*":
        return models.UnifiedVersionRange(None,
                                          [models.Restriction.all_versions()])
    semver_restrictions = semver.split("||")

    restrictions = []
    for semver_restriction in semver_restrictions:
        constraints = semver_restriction.split()
        lower_bound = None
        has_inclusive_lower = False
        upper_bound = None
        has_inclusive_upper = False
        for constraint in constraints:
            if constraint.count("<") > 1 or constraint.count(">") > 1:
                raise ValueError(
                    "semver range contains </> more than one time.")
            if constraint.startswith(operators["lte"]):
                upper_bound = constraint[2:]
                has_inclusive_upper = True
            elif constraint.startswith(operators["gte"]):
                lower_bound = constraint[2:]
                has_inclusive_lower = True
            elif constraint.startswith(operators["lt"]):
                upper_bound = constraint[1:]

            elif constraint.startswith(operators["gt"]):
                lower_bound = constraint[1:]
            else:
                upper_bound = constraint
                lower_bound = constraint
                has_inclusive_lower = True
                has_inclusive_upper = True

        lower_version = models.Version(None)
        upper_version = models.Version(None)
        if lower_bound:
            lower_version = models.Version(lower_bound)
        if upper_bound:
            upper_version = models.Version(upper_bound)
        restrictions.append(
            models.Restriction(lower_version, has_inclusive_lower,
                               upper_version, has_inclusive_upper))

    return models.UnifiedVersionRange(None, restrictions)


def not_included_versions(ordered_version_list: List[str],
                          ranges_list: List[UnifiedVersionRange]) -> List[str]:
    """
    Filter versions that are not included in the ranges.
    Versions list must be ordered to filter correctly.
    :param ordered_version_list:
    :param ranges_list:
    :return:
    """

    def _get_index(ver_lst: List[str], ver: Optional[str],
                   include: bool = False) -> int:
        """
        get index of item in list
        """
        if ver is None:
            return

        if ver in ver_lst:
            # only first one that found
            ret = ver_lst.index(ver)
        else:
            raise ValueError(
                f"Version {ver} couldn't be found in the versions list {ver_lst}")

        if include:
            ret = ret + 1
        return ret

    # FIXME: Can be set?
    rst_indices: List[set] = []
    last_index = len(ordered_version_list)
    first_index = 0
    # FIXME: remove operators
    for rng in ranges_list:
        # calculate index of the ordered_version_list slices
        # using new property `constraints` isn't necessary
        for rst in rng.constraints:
            lower, upper = rst.bounds
            if lower == upper:
                if not lower.version and not upper.version:
                    # (,) [,] - all version included
                    return []
                # Exact version range - `[VER]`
                # lower or upper versions can be taken, and inclusive set to false
                # to get the right index.
                exact_index = _get_index(ordered_version_list, lower.version)
                # exact index to be removed is added as a set to rst_indices
                rst_indices.append(set((exact_index,)))
                continue
            lower_index = _get_index(ordered_version_list, lower.version,
                                     not lower.inclusive)
            upper_index = _get_index(ordered_version_list, upper.version,
                                     upper.inclusive)
            # use of on the list and intersection .. [:]
            # [X,Y]
            if lower_index is not None and upper_index is not None:
                rst_indices.append(set(range(lower_index, upper_index)))
            # [X,]
            elif lower_index is not None and upper_index is None:
                rst_indices.append(set(range(lower_index, last_index)))
            # [,Y]
            elif lower_index is None and upper_index is not None:
                rst_indices.append(set(range(first_index, upper_index)))

    if rst_indices:
        ind_to_remove = set.union(*rst_indices)
    else:
        ind_to_remove = []

    not_included = [v for i, v in enumerate(ordered_version_list) if
                    i not in ind_to_remove]
    return not_included
