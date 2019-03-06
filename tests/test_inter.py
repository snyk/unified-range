from hypothesis import given, example, note, assume
from hypothesis.strategies import (lists, sampled_from, floats, from_regex,
                                   text, integers, sampled_from, booleans,
                                   composite)

from unified_range.api import inter

VERSIONS = [str(x) for x in range(20)]


@composite
def versions(draw):
    return draw(integers())


@composite
def lefts(draw):
    return draw(sampled_from('[('))


@composite
def rights(draw):
    return draw(sampled_from('])'))


def _check(result, left, v1=float('-inf'), v2=float('inf'), right=None):
    """
    for the range `[A,B)` to be tested with a result, call this function with:
    left='[', v1=A, v2=B, right=')'
    """
    # the inf and -inf default values are to null checks when they were not given
    # IMPORTANT: `right` must be given despite the default. This default is a python
    # limitation (otherwise we get SyntaxError). The order of arguments was
    # chosen for readability (left, v1, v2, right).
    assert right is not None
    max_version_before_range = v1 if left == '(' else v1-1
    min_version_after_range = v2 if right == ')' else v2+1
    for x in result:
        i = int(x)
        assert i <= max_version_before_range or min_version_after_range <= i


@given(v=versions())
@example(v=0)
def test_single_version_range(v):
    ranges = [f'[{v}]']
    note(ranges)
    result = inter(VERSIONS, ranges)
    assert str(v) not in result


@given(left=lefts(),
       v=versions(),
       right=rights())
def test_unbound_lower_version(left, v, right):
    ranges = [f'{left},{v}{right}']
    note(ranges)
    result = inter(VERSIONS, ranges)
    _check(result, left=left, v2=v, right=right)


@given(left=lefts(),
       v=versions(),
       right=rights())
def test_unbound_upper_version(left, v, right):
    ranges = [f'{left}{v},{right}']
    note(ranges)
    result = inter(VERSIONS, ranges)
    _check(result, left=left, v1=v, right=right)


@given(left=lefts(),
       v1=versions(),
       v2=versions(),
       right=rights())
def test_2_param_range(left, v1, v2, right):
    assume(v1 < v2)
    ranges = [f'{left}{v1},{v2}{right}']
    note(ranges)
    result = inter(VERSIONS, ranges)
    _check(result, left, v1, v2, right)

@given(left1=lefts(),
       v11=versions(),
       v12=versions(),
       right1=rights(),

       left2=lefts(),
       v21=versions(),
       v22=versions(),
       right2=rights())
def test_two_2_param_ranges(left1, v11, v12, right1,
                    left2, v21, v22, right2):
    assume(v11 < v12)
    assume(v21 < v22)

    ranges = [f'{left1}{v11},{v12}{right1}',
              f'{left2}{v21},{v22}{right2}']
    note(ranges)
    result = inter(VERSIONS, ranges)
    _check(result, left1, v11, v12, right1)
    _check(result, left2, v21, v22, right2)
