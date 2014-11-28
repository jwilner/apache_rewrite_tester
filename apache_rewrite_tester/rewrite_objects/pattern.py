import operator
import re

from apache_rewrite_tester.rewrite_objects.object import RewriteObject

__author__ = 'jwilner'


class CondPattern(RewriteObject):
    PATTERN_TYPES = LexicographicalCondPattern, IntegralCondPattern, \
        RegexCondPattern

    @staticmethod
    def get_right_pattern(string):
        """
        :type string: str
        :rtype: CondPattern
        """
        for pattern_type in CondPattern.PATTERN_TYPES:
            pattern = pattern_type.parse(string)
            if pattern is not None:
                return pattern

        return None

    def match(self, string, match_callback=None, regex_compiler=re.compile):
        """
        :type string: str
        :type match_callback: function
        :type regex_compiler: function
        :rtype: bool
        """
        raise NotImplementedError()


class RegexCondPattern(CondPattern):
    REGEX = re.compile(r"\s*(?P<negated>!?)(?P<pattern>\S+)")
    PARSERS = ('negated', bool),

    def __init__(self, negated, pattern):
        """
        :type negated: bool
        :type pattern: str
        """
        self.negated = negated
        self.pattern = pattern

    def match(self, string, match_callback=None, regex_compiler=re.compile):
        """
        :type string: str
        :type match_callback: function
        :type regex_compiler: function
        :rtype: bool
        """
        regex = regex_compiler(self.pattern)
        match = regex.match(string)

        result = match is not None
        if self.negated:
            result = not result

        # use callback only when regex matches and not negated
        if result and match is not None and callable(match_callback):
            match_callback(match)

        return result


class LexicographicalCondPattern(CondPattern):
    OPERATOR_LOOKUP = {'<': operator.lt, '>': operator.gt, '>=': operator.ge,
                       '<=': operator.le, '=': operator.eq}

    REGEX = re.compile(r"""
                       \s*(?P<negated>!?)
                       (?P<operator>>|<|>=|<=)
                       (?P<body>\w*)
                       """, re.VERBOSE)

    PARSERS = ("negated", bool), ("operator", OPERATOR_LOOKUP.get)

    def __init__(self, negated, op, body):
        """
        :type negated: bool
        :type op: function
        :type body: str
        """
        self.negated = negated
        self.operator = op
        self.body = body

    def match(self, string, match_callback=None, regex_compiler=re.compile):
        """
        :type string: str
        :type match_callback: function
        :type regex_compiler: function
        :rtype: bool
        """
        result = self.operator(string, self.body)
        return result if not self.negated else not result


class IntegralCondPattern(CondPattern):
    OPERATOR_LOOKUP = {'eq': operator.eq, 'ge': operator.ge, 'gt': operator.gt,
                       'le': operator.le, 'lt': operator.lt}

    REGEX = re.compile(r"""
                       \s*(?P<negated>!?)
                       -(?P<operator>eq|ge|gt|le|lt)
                       (?P<body>\w+)
                       """, re.VERBOSE)

    PARSERS = ("negated", bool), ("operator", OPERATOR_LOOKUP.get), \
        ("body", int)

    def __init__(self, negated, op, body):
        """
        :type negated: bool
        :type op: function
        :type body: int
        """
        self.negated = negated
        self.operator = op
        self.body = body

    def match(self, string, match_callback=None, regex_compiler=re.compile):
        """
        :type string: str
        :type match_callback: function
        :type regex_compiler: function
        :rtype: bool
        """
        result = self.operator(int(string), self.body)
        return result if not self.negated else not result