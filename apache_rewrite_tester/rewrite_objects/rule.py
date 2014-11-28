import functools
import re

from apache_rewrite_tester.context import ApacheFlag, RuleBackreference
from apache_rewrite_tester.rewrite_objects.object import RewriteObject
from apache_rewrite_tester.rewrite_objects.format_string import FormatString
from apache_rewrite_tester.rewrite_objects.pattern import RegexCondPattern

__author__ = 'jwilner'


class RewriteRule(RewriteObject):
    REGEX = re.compile(r"""
                       ^RewriteRule\s+
                       (?P<pattern>\S+)\s+
                       (?P<substitution>\S+)\s*?
                       (?:\[(?P<flags>\S+)\])?\s+$
                       """, re.VERBOSE)

    PARSERS = ("pattern", RegexCondPattern), \
              ("substitution", FormatString.parse), \
              ("flags", RuleFlag.find_all)

    def __init__(self, pattern, substitution, flags):
        """
        :type pattern: RegexCondPattern
        :type substitution: FormatString
        :type flags: frozenset[RuleFlag]
        """
        self.flags = flags
        self.pattern = pattern
        self.substitution = substitution

    def apply(self, path, context):
        """
        :type path: str
        :type context: MutableMapping
        :rtype: str
        """
        match_callback = functools.partial(RuleBackreference.update_context,
                                           context=context)

        flags = re.IGNORECASE if RuleFlag.NO_CASE in self.flags else 0
        compiler = functools.partial(re.compile, flags=flags)

        match = self.pattern.match(path, regex_compiler=compiler,
                                   match_callback=match_callback)

        if match is None:  # do not apply substitutions or flags
            return path

        new_path = self.substitution.to_string(context)

        self._apply_flags(context)

        return new_path

    def _apply_flags(self, context):
        pass


class RuleFlag(ApacheFlag):
    ESCAPE_NON_ALPHANUMERIC = "B", None
    CHAIN = "C", "chain"
    COOKIE = "CO", "cookie"
    DISCARD_PATH_INFO = "DPI", "discardpath"
    END = "END", None
    ENVIRONMENT_VARIABLE = "E", "env"
    FORBIDDEN = "F", "forbidden"
    HANDLER = "H", "Handler"
    LAST = "L", "last"
    NEXT = "N", "next"
    NO_CASE = "NC", "nocase"
    NO_ESCAPE = "NE", "noescape"
    NO_SUBREQUEST = "NS", "nosubreq"
    PROXY = "P", "proxy"
    PASSTHROUGH = "PT", "passthrough"
    QUERY_STRING_APPEND = "QSA", "qsappend"
    QUERY_STRING_DISCARD = "QSD", "qsdiscard"
    REDIRECT = "R", "redirect"
    SKIP = "S", "skip"
    TYPE = "T", "type"



