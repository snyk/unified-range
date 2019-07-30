from hypothesis import given, example, note, assume, settings, HealthCheck
from hypothesis.strategies import (sampled_from, integers, booleans,
                                   composite, data)

from unified_range import api

N = 20
# range was 0-19 but versions in ranges could be 20 which lead to value error
VERSIONS = [str(x) for x in range(N + 1)]


@composite
def versions(draw):
    return draw(integers(min_value=0, max_value=N))


@composite
def lefts(draw):
    return draw(sampled_from('[('))


@composite
def rights(draw):
    return draw(sampled_from('])'))


@composite
def range_tuples(draw):
    """
    create a random maven-style version range, returned as a tuple:
    left: opening bracket `[` or `(`
    v1: the "lower" version in the range, could be an empty string
    v2: the "upper" version in the range, could be an empty string ONLY if v1
        is not empty, or the special case `(,)` which means all versions.
    right: closing bracket `]` or `)`
    """
    left = draw(lefts())
    right = draw(rights())

    # a range must have either v1 or v2
    v1_defined = draw(booleans())
    v2_defined = draw(booleans())
    assume((v1_defined or v2_defined) or (left == "(" and right == ")"))
    v1 = draw(versions()) if v1_defined else ''
    v2 = draw(versions()) if v2_defined else ''
    # make sure v1 < v2, but only if both were defined
    assume(not v1_defined or not v2_defined or v1 < v2)

    return (left, v1, v2, right)


def range_tuple_to_str(range_tup):
    left, v1, v2, right = range_tup
    return f'{left}{v1},{v2}{right}'


def _check(result, left, v1='', v2='', right=None):
    """
    for the range `[A,B)` to be tested with a result, call this function with:
    left='[', v1=A, v2=B, right=')'
    """
    # IMPORTANT: `right` must be given despite the default. This default is a
    # python limitation (otherwise we get SyntaxError). The order of arguments
    # was chosen for readability (left, v1, v2, right).

    # the inf and -inf default values are to nullify checks when
    # versions were not given.
    if v1 == '':
        v1 = float('-inf')
    if v2 == '':
        v2 = float('inf')
    max_version_before_range = v1 if (left == '(') else v1 - 1
    min_version_after_range = v2 if right == ')' else v2 + 1
    for x in result:
        i = int(x)
        assert i <= max_version_before_range or min_version_after_range <= i


@given(v=versions())
@example(v=0)
def test_single_version_range(v):
    ranges = [f'[{v}]']
    note(ranges)
    result = api.filter_versions(VERSIONS, ranges)
    assert str(v) not in result


@given(left=lefts(),
       v=versions(),
       right=rights())
def test_unbound_lower_version(left, v, right):
    ranges = [f'{left},{v}{right}']
    note(ranges)
    result = api.filter_versions(VERSIONS, ranges)
    _check(result, left=left, v2=v, right=right)


@given(left=lefts(),
       v=versions(),
       right=rights())
def test_unbound_upper_version(left, v, right):
    ranges = [f'{left}{v},{right}']
    note(ranges)
    result = api.filter_versions(VERSIONS, ranges)
    _check(result, left=left, v1=v, right=right)


@given(left=lefts(),
       v1=versions(),
       v2=versions(),
       right=rights())
def test_2_param_range(left, v1, v2, right):
    assume(v1 < v2)
    ranges = [f'{left}{v1},{v2}{right}']
    note(ranges)
    result = api.filter_versions(VERSIONS, ranges)
    _check(result, left, v1, v2, right)


@given(left1=lefts(),
       v11=versions(),
       v12=versions(),
       right1=rights(),

       left2=lefts(),
       v21=versions(),
       v22=versions(),
       right2=rights())
@settings(suppress_health_check=(HealthCheck.filter_too_much,))
def test_two_2_param_ranges(left1, v11, v12, right1,
                            left2, v21, v22, right2):
    assume(v11 < v12)
    assume(v21 < v22)

    ranges = [f'{left1}{v11},{v12}{right1}',
              f'{left2}{v21},{v22}{right2}']
    note(ranges)
    result = api.filter_versions(VERSIONS, ranges)
    _check(result, left1, v11, v12, right1)
    _check(result, left2, v21, v22, right2)


@given(data())
@settings(suppress_health_check=(HealthCheck.filter_too_much,))
def test_many_ranges(data):
    # number of version ranges to use
    n_ranges = data.draw(integers(min_value=0, max_value=N + 1))
    rng_tuples = [data.draw(range_tuples()) for _ in range(n_ranges)]
    ranges = [range_tuple_to_str(rng) for rng in rng_tuples]
    note(ranges)
    result = api.filter_versions(VERSIONS, ranges)
    for rng in rng_tuples:
        _check(result, *rng)


@given(data=data(),
       current_version=versions())
@settings(suppress_health_check=(HealthCheck.filter_too_much,))
def test_next_filtered_version(data, current_version):
    n_ranges = data.draw(integers(min_value=0, max_value=N + 1))
    rng_tuples = [data.draw(range_tuples()) for _ in range(n_ranges)]
    ranges = [range_tuple_to_str(rng) for rng in rng_tuples]
    note(ranges)
    result = api.next_filtered_version(current_version=str(current_version),
                                       asc_versions=VERSIONS,
                                       ranges=ranges)
    if result is None:
        filtered_versions = api.filter_versions(asc_versions=VERSIONS,
                                                ranges=ranges)
        no_versions = filtered_versions == []
        # -1 is smaller than any version in VERSIONS, this is just for the code
        # not to explode in case no filtered versions were returned. In that
        # case, the `current_version_greater_than_filtered` case is irrelevant.
        max_version = filtered_versions[-1] if filtered_versions else -1
        version_too_big = int(max_version) < current_version
        assert no_versions or version_too_big
    else:
        assert int(result) >= int(current_version)


@given(data=data())
@settings(suppress_health_check=(HealthCheck.filter_too_much,))
def test_maximum_filtered_version(data):
    n_ranges = data.draw(integers(min_value=0, max_value=N + 1))
    rng_tuples = [data.draw(range_tuples()) for _ in range(n_ranges)]
    ranges = [range_tuple_to_str(rng) for rng in rng_tuples]
    note(ranges)
    result = api.maximum_filtered_version(asc_versions=VERSIONS,
                                          ranges=ranges)

    filtered_versions = api.filter_versions(asc_versions=VERSIONS,
                                            ranges=ranges)
    if result is None:
        assert not filtered_versions
    else:
        assert result == filtered_versions[-1]
