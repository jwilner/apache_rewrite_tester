import re

from apache_rewrite_tester.context import CondBackreference, \
    RuleBackreference, MapExpansion, ServerVariable
from apache_rewrite_tester.rewrite_objects.object import RewriteObject

__author__ = 'jwilner'


class TestString(RewriteObject):
    COMPONENTS = (re.compile(r"^\$(\d)"), RuleBackreference.from_string),\
        (re.compile(r"^%(\d)"), CondBackreference.from_string),\
        (re.compile(r"^\$\{(.+?)\}"), MapExpansion),\
        (re.compile(r"^%\{(.+?)\}"), ServerVariable.get)

    @classmethod
    def _parse(cls, string):
        """
        :type string: str
        :rtype: __generator[TestStringComponent|str]
        """
        while string:
            for regex, parser in cls.COMPONENTS:
                match = regex.match(string)
                if match is not None:
                    string = string[match.endpos:]
                    component = parser(match.group(1))
                    break
            else:
                component, *characters = string
                string = "".join(characters)  # unpacking makes a list, so undo

            yield component

    def __init__(self, components):
        """
        :type components: __generator[TestStringComponent|str]
        """
        self.components = tuple(components)

    def to_string(self, context):
        """
        :type context: MutableMapping
        :rtype: str
        """
        parts = []
        for component in self.components:
            try:
                part = context[component]
            except KeyError:  # it's a string
                part = component

            parts.append(part)

        return "".join(parts)
