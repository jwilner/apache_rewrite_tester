import re

from apache_rewrite_tester.context import Flag
from apache_rewrite_tester.rewrite_objects.object import RewriteObject

__author__ = 'jwilner'


class RewriteRule(RewriteObject):
    REGEX = re.compile(r"""
                       ^RewriteRule\s+
                       (?P<pattern>\S+)\s+
                       (?P<substitution>\S+)\s*?
                       (?:\[(?P<flags>\S+)\])?\s+$
                       """, re.VERBOSE)

    PARSERS = ("pattern", re.compile), \
              ("substitution", re.compile), \
              ("flags", RuleFlag.find_all)

    def __init__(self, pattern, substitution, flags):
        """
        :type pattern: __Regex
        :type substitution: __Regex
        :type flags: tuple[RuleFlag]
        """
        self.matcher = pattern
        self.rewrite = substitution
        self.flags = flags


class RuleFlag(Flag):
    ESCAPE_NON_ALPHANUMERIC = "B"
