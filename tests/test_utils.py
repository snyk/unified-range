from unified_range import utils

test_npm_semver_ranges = [
    "*", "1.2.3", "2.0.0 || 2.1.0", "<0.1.2", "<=0.12.7",
    "<5.6.5 || >=6 <6.0.1",
    "<2.0.20180219", "<1.3.0-rc.4", "<0.0.0", "<0.10.0 >=0.9.0",
    "<2.11.2 || >=3.0.0 <3.6.4 ||  >=4.0.0 <4.5.7 || >=5.0.0 <5.2.1",

]
expected_version_range = [
    '(,)', '[1.2.3]', '[2.0.0],[2.1.0]',
    '(,0.1.2)', '(,0.12.7]',
    '(,5.6.5),[6,6.0.1)', '(,2.0.20180219)',
    '(,1.3.0-rc.4)', '(,0.0.0)',
    '[0.9.0,0.10.0)',
    '(,2.11.2),[3.0.0,3.6.4),[4.0.0,4.5.7),[5.0.0,5.2.1)'
]

expected_npm_semver_range = [
    '*', '1.2.3', '2.0.0 || 2.1.0',
    '<0.1.2', '<=0.12.7',
    '<5.6.5 || >=6 <6.0.1',
    '<2.0.20180219', '<1.3.0-rc.4',
    '<0.0.0', '>=0.9.0 <0.10.0',
    '<2.11.2 || >=3.0.0 <3.6.4 || >=4.0.0 <4.5.7 || >=5.0.0 <5.2.1'
]

before_clean = [
    # npm
    "=3.0.0-rc.1",
    "=v3.7.2",
    "=5.0.2",
    ">1.2.3",
    "<=2.4",
    "<v1.2.3",
    "<=v2.4.6",
]
expected_clean_semver = [
    # npm
    '3.0.0-rc.1',
    '3.7.2',
    '5.0.2',
    '>1.2.3',
    '<=2.4',
    '<1.2.3',
    '<=2.4.6'
]
before_trim = [
    # npm
    "<  2.0.5", "< 1.12.4 || >= 2.0.0 <2.0.2", "<= 0.0.1",
    "<= 2.15.0 || >= 3.0.0 <= 3.8.2",
    ">= 0.0.10 <= 0.0.14",
    ">= 1.0.0-rc.1 <1.0.0-rc.1.1 || >= 1.0.0-rc.2 <1.0.0-rc.2.1 ",
    # # composer
    " >=8.0, <8.4.5",
    "< 1.15.2",
    ">0.7.1, <1.0.4",
    ">= 3.1, <=3.1.9",
    "< 2.1.27.9",

    # ruby
    "< 0.13.3, > 0.11.0",
    "< 0.10.0",
    "< 0.14.1.1, >= 0.13.3",
    "< 1.0.0.rc1.1",
    "< 1.3.0.pre.8",
    "<0.30.0 ,>=0.27.0",
    ">= 2.3.0, <= 2.3.10",

]
expected_comparator_trimmed = [
    '<2.0.5',
    '<1.12.4 || >=2.0.0 <2.0.2',
    '<=0.0.1',
    '<=2.15.0 || >=3.0.0 <=3.8.2',
    '>=0.0.10 <=0.0.14',
    '>=1.0.0-rc.1 <1.0.0-rc.1.1 || >=1.0.0-rc.2 <1.0.0-rc.2.1',
    # composer
    '>=8.0 <8.4.5',
    '<1.15.2',
    '>0.7.1 <1.0.4',
    '>=3.1 <=3.1.9',
    '<2.1.27.9',
    # ruby
    '<0.13.3 >0.11.0',
    '<0.10.0',
    '<0.14.1.1 >=0.13.3',
    '<1.0.0.rc1.1',
    '<1.3.0.pre.8',
    '<0.30.0 >=0.27.0',
    '>=2.3.0 <=2.3.10'

]


def test_create_from_semver():
    results = []
    for semver in test_npm_semver_ranges:
        results.append(utils.create_from_semver(semver))
    assert (expected_version_range == list(map(str, results)))


def test_transform_to_semver():
    results = []
    # using the expected results of npm to check the full conversion.
    for unified in expected_version_range:
        results.append(utils.transform_to_semver(unified))
    assert (expected_npm_semver_range == list(map(str, results)))


def test_clean_semver():
    results = []
    for semver in before_clean:
        results.append(utils._clean_semver(semver))
    assert (expected_clean_semver == results)


def test_comparator_trim():
    results = []
    for semver in before_trim:
        results.append(utils._comparator_trim(semver))
    assert (expected_comparator_trimmed == results)


def test_transform_to_semver_failure():
    results = []
    for semver in test_npm_semver_ranges:
        try:
            utils.transform_to_semver(semver)
            assert False, 'test_transform_to_semver_failure0 did not raise exception!'
        except ValueError as msg:
            assert ((str(msg) == 'Version ranges seems to already be semver')
                    or (str(msg) == 'Recommended Version is currently not supported.'))


def test_create_from_semver_failure():
    results = []
    for unified in expected_version_range:
        try:
            utils.create_from_semver(unified)
            assert False, 'test_create_from_semver_failure did not raise exception!'
        except ValueError as msg:
            assert str(
                msg) == 'Version ranges seems to already be maven version range'
