from unittest import TestCase

from apache_rewrite_tester.rewrite_objects.pattern import CondPattern, \
    RegexCondPattern, LexicographicalCondPattern, IntegralCondPattern

__author__ = 'jwilner'


class TestGetRightPattern(TestCase):
    def test_regex_pattern(self):
        pattern = CondPattern.get_right_pattern("!abcdef")
        self.assertIsInstance(pattern, RegexCondPattern)

        pattern = CondPattern.get_right_pattern("a-bcde>f")
        self.assertIsInstance(pattern, RegexCondPattern)

    def test_lexico_pattern(self):
        pattern = CondPattern.get_right_pattern("!<=abcdef")
        self.assertIsInstance(pattern, LexicographicalCondPattern)

        pattern = CondPattern.get_right_pattern(">=abcefd")
        self.assertIsInstance(pattern, LexicographicalCondPattern)

    def test_integral_pattern(self):
        pattern = CondPattern.get_right_pattern("!-le4")
        self.assertIsInstance(pattern, IntegralCondPattern)

        pattern = CondPattern.get_right_pattern("-gt9509")
        self.assertIsInstance(pattern, IntegralCondPattern)


class TestIntegralCondPattern(TestCase):
    CASES = ("-gt42", '43', True), ("!-gt42", '43', False), \
        ("-lt14", '3', True), ("-eq12093", '12093', True)

    def test_evaluates_properly(self):
        for string, input_value, result in self.CASES:
            pattern = IntegralCondPattern.parse(string)
            self.assertIs(result, pattern.match(input_value))


class TestLexicographicalCondPattern(TestCase):
    CASES = ("<ab", 'aa', True), ("=aa", "aa", True), (">ab", "ac", True), \
        ("!<ab", "aa", False), (">=ab", "ab", True)

    def test_evaluates_properly(self):
        for string, input_value, result in self.CASES:
            pattern = LexicographicalCondPattern.parse(string)
            self.assertIs(result, pattern.match(input_value))


class TestRegexCondPattern(TestCase):
    CASES = ("ab", "ab", True), ("[ab]b", "ab", True), ("a$", "ab", False), \
        ("!a$", "ab", True)

    def test_evaluates_properly(self):
        for string, input_value, result in self.CASES:
            pattern = RegexCondPattern.parse(string)
            self.assertIs(result, pattern.match(input_value))

