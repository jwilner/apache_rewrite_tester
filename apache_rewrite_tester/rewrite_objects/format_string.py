import re

from apache_rewrite_tester.environment import CondBackreference, \
    RuleBackreference, MapExpansion, ServerVariable
from apache_rewrite_tester.utils import EqualityMixin

__author__ = 'jwilner'


class FormatString(EqualityMixin):
    COMPONENTS = (re.compile(r"^\$(\d)"), RuleBackreference.from_string),\
        (re.compile(r"^%(\d)"), CondBackreference.from_string),\
        (re.compile(r"^\$\{(.+?)\}"), MapExpansion.from_string),\
        (re.compile(r"^%\{(.+?)\}"), ServerVariable.__getitem__)

    @classmethod
    def parse(cls, string):
        """
        :type string: str
        :rtype: FormatString
        """
        return cls(cls._parse(string))

    @classmethod
    def _parse(cls, string):
        """
        :type string: str
        :rtype: __generator[Hashable]
        """
        while string:
            for regex, parser in cls.COMPONENTS:
                match = regex.match(string)
                if match is not None:
                    string = string[match.end():]
                    component = parser(match.group(1))
                    break
            else:
                # woo, python 3
                component, *characters = string
                string = "".join(characters)  # unpacking makes a list, so undo

            yield component

    def __init__(self, components):
        """
        :type components: __generator[Hashable]
        """
        self.components = tuple(components)

    def format(self, environment):
        """
        :type environment: MutableMapping
        :rtype: str
        """
        parts = []
        for component in self.components:
            try:
                part = environment[component]
            except KeyError:  # it's a string
                part = component

            parts.append(part)

        return "".join(parts)
