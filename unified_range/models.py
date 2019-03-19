from attr import dataclass
from typing import List, Tuple


@dataclass
class Bound:
    version: str
    inclusive: bool = False


# FIXME: change implemntation of Version - str
class Version(object):
    def __init__(self, version):
        self.version = version

    def __str__(self):
        return f"{self.version}"

    def __eq__(self, other):
        if isinstance(other, Version):
            return self.version == other.version
        else:
            return False


class Restriction(object):

    @classmethod
    def all_versions(cls):
        return cls(Version(None), False, Version(None), False)

    # FIXME: change constructor to use `Bound`
    def __init__(self, lower_bound: Version, has_inclusive_lower: bool,
                 upper_bound: Version, has_inclusive_upper: bool):
        if not all((isinstance(lower_bound, Version),
                    isinstance(upper_bound, Version))):
            raise ValueError(
                "lower_bound and upper_bound must be of type Version")

        self.lower_bound = lower_bound
        self.has_inclusive_lower = has_inclusive_lower
        self.upper_bound = upper_bound
        self.has_inclusive_upper = has_inclusive_upper

    def __str__(self):
        buffer = ['[' if self.has_inclusive_lower else '(']
        if self.lower_bound.version:
            buffer.append(str(self.lower_bound))
        buffer.append(',')
        if self.upper_bound.version:
            buffer.append(str(self.upper_bound))
        buffer.append(']' if self.has_inclusive_upper else ')')
        # check if the versions are equals - [X.X.X,X.X.X] -> [X.X.X]
        if len(buffer) == 5 and buffer[1] == buffer[3]:
            buffer = ['[', str(self.lower_bound), ']']
        return "".join(buffer)

    def __eq__(self, other):
        if isinstance(other, Restriction):
            lower_eq = (self.lower_bound == other.lower_bound)
            upper_eq = (self.upper_bound == other.upper_bound)
            inclusive_lower_eq = (
                    self.has_inclusive_lower == other.has_inclusive_lower)
            inclusive_upper_eq = (
                    self.has_inclusive_upper == other.has_inclusive_upper)
            return lower_eq and upper_eq and inclusive_lower_eq and inclusive_upper_eq
        else:
            # fixme: raise exception
            return False

    @property
    def bounds(self) -> Tuple[Bound, Bound]:
        lower = Bound(
            version=self.lower_bound.version,
            inclusive=self.has_inclusive_lower
        )
        upper = Bound(
            version=self.upper_bound.version,
            inclusive=self.has_inclusive_upper
        )
        # FIXME: maybe handle equal lower/upper `[VER]`
        return lower, upper


class UnifiedVersionRange(object):
    # FIXME: REMOVE recommended_version feature - unused
    def __init__(self, recommended_version, restrictions):
        self.recommended_version = recommended_version
        self.restrictions = restrictions

    def __str__(self):
        if self.recommended_version is not None:
            return str(self.recommended_version)
        else:
            buffer = []
            for r in self.restrictions:
                buffer.append(str(r))
            return ",".join(buffer)

    def __eq__(self, other):
        restrictions_eq = self.restrictions == other.restrictions
        return restrictions_eq

    @property
    def constraints(self) -> List[Restriction]:
        return self.restrictions

    @staticmethod
    def parse_restriction(spec):
        has_inclusive_lower = spec.startswith("[")
        has_inclusive_upper = spec.endswith("]")
        process = spec[1:-1].strip()
        index = process.find(',')
        # [X.X.X]
        if index < 0:
            if not has_inclusive_lower or not has_inclusive_upper:
                raise ValueError(
                    "Single version must be surrounded by []: {}".format(spec))
            version = Version(process)
            restriction = Restriction(version, has_inclusive_lower, version,
                                      has_inclusive_upper)
        else:
            lower_bound = process[0: index].strip()
            upper_bound = process[index + 1:].strip()
            if lower_bound == '' and upper_bound == '':
                return Restriction.all_versions()
            if lower_bound == upper_bound:
                raise ValueError(
                    "Range cannot have identical boundaries: {}".format(spec))
            lower_version = Version(None)
            if len(lower_bound) > 0:
                lower_version = Version(lower_bound)
            upper_version = Version(None)
            if len(upper_bound) > 0:
                upper_version = Version(upper_bound)
            restriction = Restriction(lower_version, has_inclusive_lower,
                                      upper_version, has_inclusive_upper)
        return restriction

    @staticmethod
    def create_from_spec(spec: str):
        """
        Create unifiedVersionRange from maven spec string - `[x,y]`
        :param spec:
        :return:
        """
        restrictions = []
        process = spec.strip()
        version = None
        if not spec:
            return
        if not isinstance(spec, str):
            raise ValueError(
                "Only Strings allowed.\ninput spec:{}\ntype: {}".format(
                    spec,
                    type(spec)
                )
            )

        if not process.startswith(("(", "[")) and not process.endswith(
                (")", "]")):
            raise ValueError("Recommended Version is currently not supported.")
        while process.startswith("[") or process.startswith("("):
            index1 = process.find(")")
            index2 = process.find("]")
            index = index2
            if index2 < 0 or index1 < index2:
                if index1 >= 0:
                    index = index1
            if index < 0:
                raise ValueError("Unbounded range: {}".format(spec))

            restriction = UnifiedVersionRange.parse_restriction(
                process[0:index + 1])
            restrictions.append(restriction)
            process = process[index + 1:].strip()
            if len(process) > 0 and process.startswith(","):
                process = process[1:].strip()
        if len(process) > 0:
            if len(restrictions) > 0:
                raise ValueError(
                    "Only fully-qualified sets allowed in multiple set scenario: {}".format(
                        spec))
            else:
                # fixme: use strings instead Version
                version = Version(process)
                restrictions.append(Restriction.all_versions())

        return UnifiedVersionRange(version, restrictions)

    # FIXME: Remove not needed
    @staticmethod
    def create_from_version(version):
        restrictions = []
        if not isinstance(version, str):
            raise ValueError(
                "Only Strings allowed.\ninput version:{}\ntype: {}".format(
                    version, type(version)))
        return UnifiedVersionRange(Version(version), restrictions)
