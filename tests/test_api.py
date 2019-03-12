from unified_range import api


def test_semver_full_way():
    """
    1. Test conversion from semver -> unified -> semver.
    2. Validate the results against manually validated expected file.
    """
    results = []

    with open("tests/test_data/semver-ranges.txt", "r") as semver_rngs:
        semver_ranges = semver_rngs.read().splitlines()

    with open("tests/test_data/expected-semver-ranges.txt",
              "r") as expected_semver:
        expected_results = expected_semver.read().splitlines()

    for rng in semver_ranges:
        unified = api.from_semver(rng)
        semver_again = api.to_semver(str(unified))
        results.append(str(semver_again))

    assert (results == expected_results)


def test_unified_full_way():
    """
    1. Test conversion from unified -> semver -> unified.
    2. Validate the results against manually validated expected file.
    """
    results = []

    with open("tests/test_data/unified-ranges.txt", "r") as unified_rngs:
        unified_ranges = unified_rngs.read().splitlines()

    with open("tests/test_data/expected-unified-ranges.txt",
              "r") as expected_unified:
        expected_results = expected_unified.read().splitlines()

    for rng in unified_ranges:
        semver = api.to_semver(rng)
        unified = api.from_semver(str(semver))
        results.append(str(unified))

    assert (results == expected_results)
