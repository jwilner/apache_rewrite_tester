import functools
import re

from apache_rewrite_tester.environment import RuleBackreference, ApacheFlag
from apache_rewrite_tester.rewrite_objects.object import SingleLineDirective
from apache_rewrite_tester.rewrite_objects.format_string import FormatString
from apache_rewrite_tester.rewrite_objects.pattern import RegexCondPattern


__author__ = 'jwilner'


class RuleFlag(ApacheFlag):
    ESCAPE_BACKREFERENCES = r"^B$",
    CHAIN = r"^(?:C|chain)$",
    COOKIE = r"""
             ^(?:CO|cookie)=
             (?P<name>[^:]+)
             :(?P<value>[^:]+)
             :(?P<domain>[^:]+)
             (?::(?P<lifetime>[^:]+)  # optional
             (?::(?P<path>[^:]+)  # optional if lifetime included
             (?::(?P<secure>[^:]+)  # optional if path included
             (?::(?P<httponly>[^:]+)  # optional if secure included
             )?)?)?)?
             """, \
        (('lifetime', int),)
    DISCARD_PATH_INFO = r"^(?:DPI|discardpath)$",
    ENVIRONMENT_VARIABLE = r"""
                           ^(?:E|env)=
                           (?:
                           (?:(?P<variable>[^:]+):(?P<value>[^:]+))|
                           (?:!(?P<variable_to_unset>[^:]+))
                           )
                           $
                           """,
    END = r"^END$",
    FORBIDDEN = r"^(?:F|forbidden)$",
    GONE = r"^(?:G|gone)$",
    HANDLER = r"^(?:H|handler)=(?P<handler>[\w/-]+)$",
    LAST = r"^(?:L|last)$",
    NEXT = r"^(?:N|next)(?:=(?P<maximum>\w+))?$", (("maximum", int),)
    NO_CASE = r"^(?:NC|nocase)",
    NO_ESCAPE = r"^(?:NE|noescape)",
    NO_SUBREQUEST = r"^(?:NS|nosubreq)$",
    PROXY = r"^(?:P|proxy)$",
    PASS_THROUGH = r"^(?:PT|passthrough)$",
    QUERY_STRING_APPEND = r"^(?:QSA|qsappend)$",
    QUERY_STRING_DISCARD = r"^(?:QSD|qsdiscard)$",
    REDIRECT = r"""
               ^(?:R|redirect)=
               (?:
               (?P<status_code>\d{3})|
               (?P<status_name>\w+)
               )$""", \
        (('status_code', int),)
    SKIP = r"^(?:S|skip)=(?P<number>\d+)$", (('number', int),)
    TYPE = r"^(?:T|type)=(?P<content_type>[\w/-]+)$",


class RewriteRule(SingleLineDirective):
    REGEX = re.compile(r"""
                       ^RewriteRule\s+
                       (?P<pattern>\S+)\s+
                       (?P<substitution>\S+)\s*?
                       (?:\[(?P<flags>\S+)\])?\s*$
                       """, re.VERBOSE)

    PARSERS = ("pattern", RegexCondPattern.make), \
              ("substitution", FormatString.parse), \
              ("flags", RuleFlag.find_all)

    DEFAULTS = ("flags", {}),

    def __init__(self, pattern, substitution, flags):
        """
        :type pattern: RegexCondPattern
        :type substitution: FormatString
        :type flags: dict[RuleFlag, dict]
        """
        self.pattern = pattern
        self.substitution = substitution
        self.flags = flags

    def apply(self, path, environment):
        """
        :type path: str
        :type environment: MutableMapping
        :rtype: str
        """
        match_callback = functools.partial(RuleBackreference.update_environment,
                                           environment=environment)

        flags = re.IGNORECASE if RuleFlag.NO_CASE in self.flags else 0
        compiler = functools.partial(re.compile, flags=flags)

        match = self.pattern.match(path, regex_compiler=compiler,
                                   match_callback=match_callback)

        if match is None:  # do not apply substitutions or flags
            return path

        new_path = self.substitution.format(environment)

        self._apply_flags(environment)

        return new_path

    def _apply_flags(self, environment):
        """
        :type environment: MutableMapping
        """
        pass
