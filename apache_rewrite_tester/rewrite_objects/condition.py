import re
import operator

from apache_rewrite_tester.context import Flag
from apache_rewrite_tester.rewrite_objects.object import RewriteObject
from apache_rewrite_tester.rewrite_objects.test_string import TestString, \
    CondBackreference

__author__ = 'jwilner'


class RewriteCondition(RewriteObject):
    REGEX = re.compile(r"""
                       ^RewriteCond\s+
                       (?P<test_string>\S+)\s+
                       (?P<cond_pattern>\S+)\s*?
                       (?:\[(?P<flags>\S+)\])?\s+$
                       """, re.VERBOSE)

    PARSERS = ("test_string", TestString.parse), \
              ("cond_pattern", CondPattern.parse), \
              ("flags", ConditionFlag.find_all)

    @classmethod
    def chain(cls, rewrite_conditions, context):
        """
        :type rewrite_conditions: Iterable[RewriteCondition]
        :rtype: bool
        """
        status = True
        
        for rewrite_condition in rewrite_conditions:
            status = rewrite_condition.evaluate(context)

            if ConditionFlag.OR_NEXT in rewrite_condition.flags:
                if status:
                    return True
                else:
                    continue

            if not status:
                return False

        return status



    def __init__(self, test_string, cond_pattern, flags):
        """
        :type test_string: TestString
        :type cond_pattern: CondPattern
        :type flags: tuple[ConditionFlag]
        """
        self.test_string = test_string
        self.condition = cond_pattern
        self.flags = flags

    def evaluate(self, context):
        """
        :type context: MutableMapping
        :rtype: bool
        """
        string = self.test_string.to_string(context)
        return self.condition.match(string, context, self.flags)


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

    def match(self, string, context, flags):
        """
        :type string:
        :type context: MutableMapping
        :type flags: tuple[ConditionFlag]
        :rtype: bool
        """
        raise NotImplementedError()


class RegexCondPattern(CondPattern):
    REGEX = re.compile(r"\s*(?P<negated>!?)(?P<pattern>\S+)")
    PARSERS = ('negated', bool), ('pattern', re.compile)

    def __init__(self, negated, pattern):
        """
        :type negated: bool
        :type pattern: __Regex
        """
        self.negated = negated
        self.regex = pattern

    def match(self, string, context, flags):
        """
        Updates context if it matches and isn't negated. Wipes out
        all previous ConfBackReferences

        :type string: str
        :type context: MutableMapping
        :type flags: tuple[ConditionFlag]
        :rtype: bool
        """
        match = self.regex.match(string)

        result = match is not None
        if self.negated:
            result = not result

        # update state only when regex matches and not negated
        if result and match is not None:
            for index in range(10):
                backreference = CondBackreference(index)
                try:
                    group = match.group(index)
                    context[backreference] = group
                except IndexError:
                    # unset old backreferences
                    try:
                        del context[backreference]
                    except KeyError:
                        # won't be any for higher indices
                        break

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

    def match(self, string, context, flags):
        """
        Doesn't update context

        :type string: str
        :type context: MutableMapping
        :type flags: tuple[ConditionFlag]
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
        Doesn't update context

        :type negated: bool
        :type op: function
        :type body: int
        """
        self.negated = negated
        self.operator = op
        self.body = body

    def match(self, string, context, flags):
        """
        :type string: str
        :type context: MutableMapping
        :type flags: tuple[ConditionFlag]
        :rtype: bool
        """
        result = self.operator(int(string), self.body)
        return result if not self.negated else not result


class ConditionFlag(Flag):
    NO_CASE = "NC", "nocase"
    OR_NEXT = "OR", "ornext"
    NO_VARY = "NV", "novary"
