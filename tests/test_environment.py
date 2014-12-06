from unittest import TestCase

from apache_rewrite_tester.environment import Backreference, CondBackreference, \
    RuleBackreference

__author__ = 'jwilner'


class FakeMatch(object):
    def __init__(self, groups=()):
        """
        :type groups: tuple[str]
        """
        self._groups = groups

    def group(self, index):
        """
        :type index: int
        :rtype: str
        """
        return self._groups[index]


class TestUpdateEnvironment(TestCase):
    def test_sets_properly(self):
        mapping = {}
        match = FakeMatch(tuple('abc'))

        Backreference.update_environment(match, mapping)

        backs = dict(zip(map(Backreference, range(3)), "abc"))

        self.assertEqual(3, len(mapping))
        self.assertDictEqual(backs, mapping)

    def test_unsets_expectedly(self):
        mapping = dict(zip(map(Backreference, range(10)), "abcdefghij"))
        expected = dict(zip(map(Backreference, range(4)), "abcde"))
        match = FakeMatch(tuple("abcd"))

        Backreference.update_environment(match, mapping)

        self.assertEqual(4, len(mapping))
        self.assertDictEqual(expected, mapping)

    def test_hashes_work_properly(self):
        mapping = dict(list(zip(map(CondBackreference, range(4)), "abcd")) +
                       list(zip(map(RuleBackreference, range(4)), "abcd")))

        self.assertEqual(8, len(mapping))
