import unittest

from apache_rewrite_tester.rewrite_objects.format_string import FormatString
from apache_rewrite_tester.context import RuleBackreference, CondBackreference

__author__ = 'jwilner'


class TestFormatStringParsing(unittest.TestCase):
    def test_consumes_properly(self):
        string = "$1$2%0%1"
        components = tuple(list(map(RuleBackreference, range(1, 3))) +
                           list(map(CondBackreference, range(2))))

        parsed = FormatString.parse(string)

        self.assertSequenceEqual(components, parsed.components)

    def test_handles_characters(self):
        string = "$1$2a%0%1"
        components = tuple(list(map(RuleBackreference, range(1, 3))) +
                           list("a") +
                           list(map(CondBackreference, range(2))))

        parsed = FormatString.parse(string)

        self.assertSequenceEqual(components, parsed.components)

