import re
from unified_version import models


def _clean_semver(semver):
    # also cleaning `v=X.X.X` `= X.X.X`
    # fixme: regex catching not valid semvers `<=v1.2.3` => `<1.2.3'
    remove_eq = re.sub(r'(?<![<>])=?v?(?=.*?)', '', semver.strip())
    remove_eq_v = re.sub(r'(?<=[<>])v?(?=.*?)', '', remove_eq)
    return remove_eq_v


def _comparator_trim(semver):
    """
    clean spaces between operator to the version.
    `> 1.2.3 <= 1.2.5` => `>1.2.3 <=1.2.5`
    :param semver:
    :return:
    """
    # switch `,` to ` ` for composer versions
    if ',' in semver:
        semver = semver.replace(',', ' ')
    # fixme: check regex catching all data.
    COMPARTOR_TRIM = r'\s+(?=[^<>|])'
    return re.sub(COMPARTOR_TRIM, '', semver.strip())


def transform_to_semver(unified_spec):
    """
    npm spec list[">=16.0.0 <16.0.6", ">=16.1.0 <16.1.2", ">=16.2.0 <16.2.1", ">=16.3.0 <16.3.3", ">=16.4.0 <16.4.2"]
    unified        (16.0.0,], [,16.0.6]
                    (16.0.0,16.0.1]
    :param semver:
    :return: string
    """
    operators = {"lt": "<", "lte": "<=", "gt": ">", "gte": ">="}
    contains_all_version = models.UnifiedVersionRange(None, [
        models.Restriction.all_versions()])
    unified_version = models.UnifiedVersionRange.create_from_spec(unified_spec)
    # fixme: return for `120 ==> * ==> (,)`
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
                # fixme: return here
                raise ValueError("lower and upper bound are None")
    return " || ".join(semvers)


def create_from_semver(semver):
    """
    npm spec ||  ">=16.0.0 <16.0.6", ">=16.1.0 <16.1.2", ">=16.2.0 <16.2.1", ">=16.3.0 <16.3.3", ">=16.4.0 <16.4.2"
    npm spec list[">=16.0.0 <16.0.6", ">=16.1.0 <16.1.2", ">=16.2.0 <16.2.1", ">=16.3.0 <16.3.3", ">=16.4.0 <16.4.2"]
    one restriction >=16.0.0 <16.0.6"
    unified        (16.0.0,], [,16.0.6]
                    (16.0.0,16.0.1]
    :param semver:
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
