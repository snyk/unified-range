from itertools import chain

import pytest
from hypothesis import given, example, note, assume, settings, HealthCheck
from hypothesis.strategies import integers, data

from unified_range import api

from tests.test_utils import (N, VERSIONS, versions, lefts, rights,
                              range_tuples, range_tuple_to_str)


# ENTRY POINT (for the test logic)
def check(input_ranges, result):
    """
    This function verifies the behaviour of merge_versions *UNDER THE
    SIMPLIFYING CONDITION* that versions are consecutive integers
    (see test_utils.VERSIONS).
    It is a non-generic implementation, testing the generic one.
    See a similar use-case on test_filter_versions.py
    """
    for rng in set(input_ranges):
        [own_group] = [grp for grp in result if rng in grp]
        other_groups = [grp for grp in result if rng not in grp]
        # 1. verify intersection with all ranges in the resulting merged group
        for sister_range in own_group:
            if sister_range == rng:
                continue
            assert _intersecting(rng, sister_range)
        # 2. verify this range has NO intersection with any of the ranges
        #    outside of its merged group.
        for foreign_range in chain.from_iterable(other_groups):
            assert not _intersecting(rng, foreign_range)


def _intersecting(rng1, rng2):
    if _single_version(rng1):
        return _intersecting_single_version(rng1, rng2)
    elif _single_version(rng2):
        return _intersecting_single_version(rng2, rng1)
    elif _empty_range(rng1) or _empty_range(rng2):
        # an empty range has no intersections
        return False
    elif _all_versions(rng1) or _all_versions(rng2):
        # we know that no range is empty
        return True

    left1, (v11, v12), right1 = rng1[0], rng1[1:-1].split(','), rng1[-1]
    left2, (v21, v22), right2 = rng2[0], rng2[1:-1].split(','), rng2[-1]
    # ONLY FOR THE TESTS - versions are integers, empty ones are +- inf
    # "start" versions
    v11 = float('-inf') if v11 == "" else int(v11)
    v21 = float('-inf') if v21 == "" else int(v21)
    # "end" versions
    v12 = float('inf') if v12 == "" else int(v12)
    v22 = float('inf') if v22 == "" else int(v22)

    # no intersection is easier to find since it is just 2 symmetric
    # simple cases, where one of the ranges starts and ends before the other
    # starts.
    # for a range to start and end before another range, its end (v2) must be
    # smaller than the other range's start (v1)
    no_intersection = (
        # rng1 is "smaller" than rng2:
        v12 < v21 or
        (v12 == v21 and right1 == ')') or
        (v12 == v21 and left2 == '(') or

        # rng2 is "smaller" than rng1:
        v22 < v11 or
        (v22 == v11 and right2 == ')') or
        (v22 == v11 and left1 == '('))

    # we have an intersections if we ruled out all options for "no intersection"
    return not no_intersection


def _single_version(rng):
    return not _empty_range(rng) and rng[0] == '[' and rng[-1] == ']' and ',' not in rng


def _empty_range(rng):
    "[] and () are the empty ranges"
    return (len(rng) == 2 and rng[0] in ('(', '[') and rng[-1] in (')', ']'))


def _all_versions(rng):
    # (,) or [,] or (,] or [,)
    return (rng[0] in ('(', '[') and
            rng[1] == ',' and
            rng[2] in (')', ']'))


def _intersecting_single_version(single_version_range, rng):
    v = int(single_version_range[1:-1])
    if _single_version(rng):
        # 2 single version ranges, must be equal and valid
        return v == int(rng[1:-1])

    left, (v1, v2), right = rng[0], rng[1:-1].split(','), rng[-1]
    v1 = float('-inf') if v1 == "" else int(v1)
    v2 = float('inf') if v2 == "" else int(v2)

    if v < v1:                  # (1)
        return False
    elif v == v1:               # (2)
        return left == '['
    else:  # v > v1:            # (3)
        return v < v2 or (v == v2 and right == ']')
    # implied: v > v2 -> False


@pytest.mark.parametrize("ranges,expected", [
    (["[1,2]", "[3,4]"], False),
    (["[1,3]", "[2, 4]"], True),
    (["[1,6]", "[2, 4]"], True),
    (["[2,3]", "[2, 3]"], True),
    (["[5]", "(1,8)"], True),
    (["[5]", "[1,8)"], True),
    (["[5]", "(1,8]"], True),
    (["[5]", "[1,8]"], True),
    (["[5]", "[1,5]"], True),
    (["[5]", "[1,5)"], False),
    (["[5]", "[1,4]"], False),
    (["[5]", "(,5)"], False),
    (["[5]", "[6,7]"], False),
    (["[5]", "(5,8]"], False),
    (["[5]", "(,8]"], True),
    (["[5]", "[5]"], True),
    (["[5]", "[4]"], False),
    (["[1,2]", "(2,4]"], False),
    (["[4,7]", "[2,4)"], False),
    (["[1,2]", "(2,4]"], False),
    (["[1,2)", "(2,4]"], False),
    (["[1,2)", "[2,4]"], False),
    (["[1,6]", "[2, 4]"], True),
    (["(2,8)", "[]"], False),
    (["(,)", "[1,2]"], True),
    (["(,)", "[1]"], True),
    (["(,)", "[]"], False),
])
def test__intersecting(ranges, expected):
    # it's a complicated function, better test it to know the tests work :))
    assert _intersecting(*ranges) == expected
    assert _intersecting(*reversed(ranges)) == expected


# real tests start here
@pytest.mark.parametrize("ranges,expected", [
    (["[1,5]", "[2,3]"], ({"[1,5]", "[2,3]"})),
    (["[1,5]", "[6,10]"], ({"[1,5]"}, {"[6,10]"})),
    (["[1,5]", "[2,3]", "[6,10]"], ({"[1,5]", "[2,3]"}, {"[6,10]"})),
    (["[7,12]", "[1,5]", "[2,3]", "[6,10]"],
     ({"[1,5]", "[2,3]"}, {"[6,10]", "[7,12]"})),
])
def manual_tests(ranges, expected):
    result = api.merge_ranges(asc_versions=VERSIONS, ranges=ranges)
    # result order is random, so comparing both ways to get equality
    for group in result:
        assert group in expected

    for group in expected:
        assert group in result

    check(ranges, result)       # FIXME: not needed


# TODO: hypothesis tests, now that the `check` function is ready.
@given(data())
@settings(suppress_health_check=(HealthCheck.filter_too_much,))
def test_merge_versions(data):
    # number of version ranges to use
    n_ranges = data.draw(integers(min_value=0, max_value=N + 1))
    rng_tuples = [data.draw(range_tuples()) for _ in range(n_ranges)]
    ranges = [range_tuple_to_str(rng) for rng in rng_tuples]
    note(ranges)
    result = api.merge_ranges(asc_versions=VERSIONS, ranges=ranges)
    check(ranges, result)
