import re
from typing import Optional, List

from unified_range import models

from unified_range.models import UnifiedVersionRange


def is_semver_range(rng):
    semver_operators = {"lt": "<", "lte": "<=", "gt": ">", "gte": ">="}
    return any(op in rng for op in semver_operators.values())


def is_unified_range(rng):
    unified_operators = {"lt": ")", "lte": "]", "gt": "(", "gte": "["}
    return any(op in rng for op in unified_operators.values())


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


# def not_included_versions(versions: List[str],
#                           unified_ranges: List[UnifiedVersionRange]
#                           ) -> List[str]:
#     """
#     return the intersection of the versions list and the version ranges.
#     versions should be ordered.
#     :param versions, versions_ranges
#     :return: version list
#     """
#     versions_list = versions
#     for unif_rng in unified_ranges:
#         for rest in unif_rng.restrictions
#             semver = semver.replace(',', ' ')
#     not_included_versions = []
#     COMPARTOR_TRIM = r'\s+(?=[^<>|])'
#     return not_included_versions
#

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
    operators = {"lt": "<", "lte": "<=", "gt": ">", "gte": ">="}
    contains_all_version = models.UnifiedVersionRange(None, [
        models.Restriction.all_versions()])
    unified_version = models.UnifiedVersionRange.create_from_spec(unified_spec)
    if unified_version == contains_all_version:
        return "*"

    unified_restrictions = unified_version.restrictions
    semvers = []

    for restriction in unified_restrictions:
        if restriction.upper_bound and restriction.lower_bound:
            # specific version
            if restriction.lower_bound == restriction.upper_bound:
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
            if restriction.upper_bound and not restriction.lower_bound:
                lt_lte = operators["lt"]
                if restriction.has_inclusive_upper:
                    lt_lte = operators["lte"]
                semvers.append(
                    "{}{}".format(lt_lte, restriction.upper_bound))
            elif restriction.lower_bound and not restriction.upper_bound:
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
        lower_version = None
        upper_version = None
        if lower_bound:
            lower_version = models.Version(lower_bound)
        if upper_bound:
            upper_version = models.Version(upper_bound)
        restrictions.append(
            models.Restriction(lower_version, has_inclusive_lower,
                               upper_version, has_inclusive_upper))
    return models.UnifiedVersionRange(None, restrictions)


def not_inculded_versions(ordered_version_list: List[str],
                          ranges_list: List[UnifiedVersionRange]):
    """

    :param ordered_version_list:
    :param ranges_list:
    :return:
    """

    def _get_index(lst: List[str], item: str, include: bool = False) -> int:
        """
        get index of item in list
        """
        ret = None
        try:
            # only first one that found
            ret = lst.index(item)
        except ValueError as e:
            print(f"item {item} couldn't be found in the list")
            # raise ValueError(f"item {item} couldn't be found in the list")

        if ret and include:
            ret = ret + 1
        return ret

    included_indexes = []
    last_index = len(ordered_version_list) - 1
    first_index = 0
    # FIXME: remove operators
    for rng in ranges_list:
        # calculate index of the ordered_version_list slices
        # using new property `constraints` isn't necessary
        for rst in rng.constraints:
            import pudb
            pudb.set_trace()
            lower, upper = rst.bounds
            lower_index = _get_index(ordered_version_list, str(lower[0]),
                                     lower[1])
            upper_index = _get_index(ordered_version_list, str(upper[0]),
                                     upper[1])
            # use of on the list and intersection .. [:]
            print({str(upper[0]): upper_index,str(lower[0]): lower_index})
            if lower_index and upper_index:
                included_indexes.append(set(range(lower_index, upper_index)))
            elif lower_index and not upper_index:
                included_indexes.append(set(range(lower_index, last_index)))
            elif not lower_index and upper_index:
                included_indexes.append(set(range(first_index, upper_index)))
            else:
                continue
    if included_indexes:
        ind_to_remove = set.union(*included_indexes)
    else:
        ind_to_remove = []
    not_included = [v for i, v in enumerate(ordered_version_list) if
                    i not in ind_to_remove]
    return not_included
