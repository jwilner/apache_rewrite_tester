import re

from apache_rewrite_tester.rewrite_objects.object import ContextDirective
from apache_rewrite_tester.rewrite_objects.condition import RewriteCondition
from apache_rewrite_tester.rewrite_objects.rule import RewriteRule
from apache_rewrite_tester.rewrite_objects.simple_directives import \
    RewriteEngine, ServerName

__author__ = 'jwilner'

IP_WILDCARDS = {'*', "__default__"}  # will replace with None


def _parse_apache_ip_string_with_wildcards(string):
    """
    :type string: str
    :rtype: str
    """
    return None if string in IP_WILDCARDS else string.strip("[]")


def _parse_port(string):
    """
    :type string: str
    :rtype: int
    """
    return int(string) if string.isdigit() else None


class VirtualHost(ContextDirective):
    START_REGEX = re.compile(r"""
                             <VirtualHost\s+
                             (?P<ip>
                             \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|  # IPv4
                             \[(?:[A-F\d]{1,4}:){7}[A-F\d]{1,4}\]|  # or IPv6
                             \*|_default_  # or wildcards
                             ?)
                             (?::(?P<port>\d{1,5}|\*))>
                             """, re.VERBOSE)

    END_REGEX = re.compile(r"</VirtualHost>")

    PARSERS = ("ip", _parse_apache_ip_string_with_wildcards), \
        ("port", _parse_port)

    DEFAULTS = ('port', None),

    INNER_DIRECTIVE_TYPES = RewriteCondition, RewriteRule, ServerName, \
        RewriteEngine

    def __init__(self, ip, port, children):
        """
        :type ip: str
        :type port: int
        :type children: tuple[SingleLineDirective]
        """
        super(VirtualHost, self).__init__(children)
        self.ip = ip
        self.port = port
        # blows up if no server name or too many
        self.server_name, = (directive for directive in children
                             if isinstance(directive, ServerName))

    def apply(self, path, environment):
        """
        :type path: str
        :type environment: MutableMapping
        :rtype: str
        """
        pass
