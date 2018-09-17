from unittest import skip
from unittest import TestCase

from unified_range import models
from unified_range import utils
from unified_range import api


@skip
class ModelsTestCase(TestCase):
    def setUp(self):
        pass

    def test_parse_restrictions(self):
        # TODO
        pass

    def test_create_from_restrictions(self):
        pass


class UtilsTestCase(TestCase):
    def setUp(self):
        self.test_npm_semver_ranges = [
            "*", "1.2.3", "2.0.0 || 2.1.0", "<0.1.2", "<=0.12.7",
            "<5.6.5 || >=6 <6.0.1",
            "<2.0.20180219", "<1.3.0-rc.4", "<0.0.0", "<0.10.0 >=0.9.0",
            "<2.11.2 || >=3.0.0 <3.6.4 ||  >=4.0.0 <4.5.7 || >=5.0.0 <5.2.1",

        ]
        self.expected_version_range = [
            '(,)', '[1.2.3]', '[2.0.0],[2.1.0]',
            '(,0.1.2)', '(,0.12.7]',
            '(,5.6.5),[6,6.0.1)', '(,2.0.20180219)',
            '(,1.3.0-rc.4)', '(,0.0.0)',
            '[0.9.0,0.10.0)',
            '(,2.11.2),[3.0.0,3.6.4),[4.0.0,4.5.7),[5.0.0,5.2.1)'
        ]
        # fixme:
        self.expected_npm_semver_range = [
            '*', '1.2.3', '2.0.0 || 2.1.0',
            '<0.1.2', '<=0.12.7',
            '<5.6.5 || >=6 <6.0.1',
            '<2.0.20180219', '<1.3.0-rc.4',
            '<0.0.0', '>=0.9.0 <0.10.0',
            '<2.11.2 || >=3.0.0 <3.6.4 || >=4.0.0 <4.5.7 || >=5.0.0 <5.2.1'
        ]

        self.before_clean = [
            # npm
            "=3.0.0-rc.1",
            "=v3.7.2",
            "=5.0.2",
            ">1.2.3",
            "<=2.4",
            "<v1.2.3",
            "<=v2.4.6",
        ]
        self.expected_clean_semver = [
            # npm
            '3.0.0-rc.1',
            '3.7.2',
            '5.0.2',
            '>1.2.3',
            '<=2.4',
            '<1.2.3',
            '<=2.4.6'
        ]
        self.before_trim = [
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
        self.expected_comparator_trimmed = [
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

    def test_create_from_semver(self):
        results = []
        for semver in self.test_npm_semver_ranges:
            results.append(utils.create_from_semver(semver))
        # print(list(map(str, results)))
        # self.assertIsNotNone(results)
        self.assertEqual(self.expected_version_range, list(map(str, results)))

    def test_transform_to_semver(self):
        results = []
        # using the expected results of npm to check the full conversion.
        for unified in self.expected_version_range:
            results.append(utils.transform_to_semver(unified))
        # self.assertIsNotNone(results)
        self.assertEqual(self.expected_npm_semver_range,
                         list(map(str, results)))
        # fixme: change in order of the constraints, good?
        # self.assertEqual(self.test_npm_semver_ranges,
        #                  list(map(str, results)))

    def test_clean_semver(self):
        results = []
        for semver in self.before_clean:
            results.append(utils._clean_semver(semver))
        self.assertEqual(self.expected_clean_semver, results)

    def test_comparator_trim(self):
        results = []
        for semver in self.before_trim:
            results.append(utils._comparator_trim(semver))
        # print(results)
        self.assertEqual(self.expected_comparator_trimmed, results)


@skip
# fixme: add expected result data
class APITestCase(TestCase):
    def setUp(self):
        self.test_npm_semvers = []

    def test_npm_full_way(self):
        results = []

        with open("test_data/npm/npm-semver.lst.uniq", "r") as npm:
            npm_ranges = list(map(lambda s: s.strip(), list(npm)))

        for range in npm_ranges:
            unified = api.from_semver(range)
            semver_again = api.to_semver(str(unified))
            results.append(str(semver_again))
        self.assertEqual(results, npm_ranges)

    def test_maven_full_way(self):
        results = []

        with open("test_data/maven/maven-range.lst.uniq", "r") as maven:
            maven_ranges = list(map(lambda s: s.strip(), list(maven)))

        for range in maven_ranges:
            # try:
            semver = api.to_semver(range)
            unified = api.from_semver(str(semver))
            results.append(str(unified))
            # print(
            #     "{} ==> {} ==> {}".format(line.strip(), unified,
            #                               semver_again))
        self.assertalEqual(results, maven_ranges)
        # except Exception as e:
        #     print("Exception: {}, Version range: {}".format(e, line))

    def test_nuget_full_way(self):
        results = []

        with open("test_data/nuget/nuget-maven-range.lst.uniq", "r") as nuget:
            nuget_ranges = list(map(lambda s: s.strip(), list(nuget)))

        for range in nuget_ranges:
            # try:
            semver = api.to_semver(range)
            unified = api.from_semver(str(semver))
            results.append(str(unified))
            # print(
            #     "{} ==> {} ==> {}".format(line.strip(), unified,
            #                               semver_again))
        self.assertEqual(results, nuget_ranges)
        # except Exception as e:
        #     print("Exception: {}, Version range: {}".format(e, line))

    def test_pip_full_way(self):
        results = []

        with open("test_data/pip/pip-maven-range.lst.uniq", "r") as pip:
            pip_ranges = list(map(lambda s: s.strip(), list(pip)))

        for range in pip_ranges:
            # try:
            semver = api.to_semver(range)
            unified = api.from_semver(str(semver))
            results.append(str(unified))
            # print(
            #     "{} ==> {} ==> {}".format(line.strip(), unified,
            #                               semver_again))
        self.assertEqual(results, pip_ranges)
        # except Exception as e:
        #     print("Exception: {}, Version range: {}".format(e, line))
