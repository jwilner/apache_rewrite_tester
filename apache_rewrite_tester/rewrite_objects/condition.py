import functools
import re

from apache_rewrite_tester.context import ApacheFlag, CondBackreference
from apache_rewrite_tester.rewrite_objects.format_string import FormatString
from apache_rewrite_tester.rewrite_objects.object import RewriteObject
from apache_rewrite_tester.rewrite_objects.pattern import CondPattern


__author__ = 'jwilner'


class RewriteCondition(RewriteObject):
    REGEX = re.compile(r"""
                       ^RewriteCond\s+
                       (?P<test_string>\S+)\s+
                       (?P<cond_pattern>\S+)\s*?
                       (?:\[(?P<flags>\S+)\])?\s+$
                       """, re.VERBOSE)

    PARSERS = ("test_string", FormatString.parse), \
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
        :type test_string: FormatString
        :type cond_pattern: CondPattern
        :type flags: dict[ConditionFlag, dict]
        """
        self.flags = flags
        self.test_string = test_string
        self.condition = cond_pattern

    def evaluate(self, context):
        """
        :type context: MutableMapping
        :rtype: bool
        """
        string = self.test_string.format(context)
        context_updater = functools.partial(CondBackreference.update_context,
                                            context=context)

        flags = re.IGNORECASE if ConditionFlag.NO_CASE in self.flags else 0
        compiler = functools.partial(re.compile, flags=flags)

        return self.condition.match(string, regex_compiler=compiler,
                                    match_callback=context_updater)


class ConditionFlag(ApacheFlag):
    NO_CASE = r"^(?:NC|nocase)$",
    OR_NEXT = r"^(?:OR|ornext)$",
    NO_VARY = r"^(?:NV|novary)$",