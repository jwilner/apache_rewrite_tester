import re

from apache_rewrite_tester.rewrite_objects.object import SingleLineDirective

__author__ = 'jwilner'


class ServerName(SingleLineDirective):
    REGEX = re.compile(r"ServerName\s+(?P<server_name>\S+)")

    def __init__(self, server_name):
        self._value = server_name

    def __eq__(self, other):
        """
        Compare safely with other ServerNames, else compare as string
        """
        if isinstance(other, self.__class__):
            return other._value == self._value

        return other == self._value


class RewriteEngine(SingleLineDirective):
    REGEX = re.compile(r"RewriteEngine\s+(?P<status>on|off)")

    @classmethod
    def get_default(cls):
        return RewriteEngine("off")

    def __init__(self, status):
        self.on = status == "on"
