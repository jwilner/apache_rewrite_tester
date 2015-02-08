import functools
import re
import operator
from apache_rewrite_tester.rewrite_objects.ip_and_port import IpWildcardPattern

from apache_rewrite_tester.rewrite_objects.object import SingleLineDirective


__author__ = 'jwilner'


class RewriteEngine(SingleLineDirective):
    REGEX = re.compile(r"RewriteEngine\s+(?P<on>on|off)")

    PARSERS = ("on", functools.partial(operator.eq, "on")),

    @classmethod
    def get_default(cls):
        return RewriteEngine(False)

    def __init__(self, on):
        """
        :type on: bool
        """
        self.on = on


class ServerName(SingleLineDirective):
    REGEX = re.compile(r"ServerName\s+(?P<server_name>\S+)")

    def __init__(self, server_name):
        self.server_name = server_name


class NameVirtualHost(SingleLineDirective):
    REGEX = re.compile(r"NameVirtualHost\s+(?P<ip_address>\S+)")

    PARSERS = ("ip_address", IpWildcardPattern.make)
