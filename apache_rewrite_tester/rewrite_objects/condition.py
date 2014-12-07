import functools
import re

from apache_rewrite_tester.environment import ApacheFlag, CondBackreference
from apache_rewrite_tester.rewrite_objects.format_string import FormatString
from apache_rewrite_tester.rewrite_objects.object import SingleLineDirective
from apache_rewrite_tester.rewrite_objects.pattern import CondPattern


__author__ = 'jwilner'


class ConditionFlag(ApacheFlag):
    NO_CASE = r"^(?:NC|nocase)$",
    OR_NEXT = r"^(?:OR|ornext)$",
    NO_VARY = r"^(?:NV|novary)$",


class RewriteCondition(SingleLineDirective):
    REGEX = re.compile(r"""
                       ^RewriteCond\s+
                       (?P<test_string>\S+)\s+
                       (?P<cond_pattern>\S+)
                       (?:\s+\[(?P<flags>\S+)\])?$
                       """, re.VERBOSE)

    PARSERS = ("test_string", FormatString.parse), \
              ("cond_pattern", CondPattern.get_right_pattern), \
              ("flags", ConditionFlag.find_all)

    DEFAULTS = ("flags", {}),

    @classmethod
    def chain(cls, rewrite_conditions, environment):
        """
        :type rewrite_conditions: Iterable[RewriteCondition]
        :rtype: bool
        """
        status = True

        for rewrite_condition in rewrite_conditions:
            status = rewrite_condition.evaluate(environment)

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
        :type test_string: FormatString
        :type cond_pattern: CondPattern
        :type flags: dict[ConditionFlag, dict]
        """
        self.flags = flags
        self.test_string = test_string
        self.cond_pattern = cond_pattern

    def evaluate(self, environment):
        """
        :type environment: MutableMapping
        :rtype: bool
        """
        string = self.test_string.format(environment)
        environment_updater = \
            functools.partial(CondBackreference.update_environment,
                              environment=environment)

        flags = re.IGNORECASE if ConditionFlag.NO_CASE in self.flags else 0
        compiler = functools.partial(re.compile, flags=flags)

        return self.cond_pattern.match(string, regex_compiler=compiler,
                                       match_callback=environment_updater)
