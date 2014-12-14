import re
from apache_rewrite_tester.rewrite_objects.context import ContextDirective

from apache_rewrite_tester.rewrite_objects.condition import RewriteCondition
from apache_rewrite_tester.rewrite_objects.rule import RewriteRule
from apache_rewrite_tester.rewrite_objects.simple_directives import \
    RewriteEngine, ServerName

__author__ = 'jwilner'

IP_WILDCARD = "*"
PORT_WILDCARD = 0

IP_WILDCARDS = {'*', "__default__"}  # will replace with None


def _parse_apache_ip_string_with_wildcards(string):
    """
    :type string: str
    :rtype: str
    """
    return IP_WILDCARD if string in IP_WILDCARDS else string.strip("[]")


def _parse_port(string):
    """
    :type string: str
    :rtype: int
    """
    return int(string) if string.isdigit() else PORT_WILDCARD


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

    STRICT_MATCH, WILDCARD_MATCH, NO_MATCH = range(3)

    def __init__(self, ip, port, children):
        """
        :type ip: str
        :type port: int
        :type children: tuple[SingleLineDirective]
        """
        super(VirtualHost, self).__init__(children)
        self.ip = ip
        self.port = port

        # blows up if too many but use defaults
        self.server_name, = [directive for directive in children
                             if isinstance(directive, ServerName)] or (None,)

        self.rewrite_engine, = \
            [directive for directive in children
             if isinstance(directive, RewriteEngine)] \
            or (RewriteEngine.get_default(),)

    def match_request(self, ip, port, requested_hostname,
                      default_server_name):
        """
        :type ip: str
        :type port: int|str
        :type requested_hostname: str
        :type default_server_name: str
        :rtype: (int, int)
        """
        ip_match, port_match, hostname_match = (self.NO_MATCH,) * 2

        if ip == self.ip:
            ip_match = self.STRICT_MATCH
        elif self.ip == IP_WILDCARD:
            ip_match = self.WILDCARD_MATCH

        if IP_WILDCARD in {self.port, port}:
            port_match = self.WILDCARD_MATCH
        elif port == self.port:
            port_match = self.STRICT_MATCH

        # only as good as its weakest link
        ip_port_match = max(ip_match, port_match)

        server_name = self.server_name \
            if self.server_name is not None \
            else default_server_name

        if requested_hostname == server_name:
            hostname_match = self.STRICT_MATCH

        return ip_port_match, hostname_match