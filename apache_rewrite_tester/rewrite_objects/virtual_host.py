import re

from apache_rewrite_tester.rewrite_objects.context import ContextDirective, \
    RequestHandler
from apache_rewrite_tester.rewrite_objects.condition import RewriteCondition
from apache_rewrite_tester.rewrite_objects.ip_and_port import \
    PortWildcardPattern, IpWildcardPattern
from apache_rewrite_tester.rewrite_objects.rule import RewriteRule
from apache_rewrite_tester.rewrite_objects.simple_directives import \
    RewriteEngine, ServerName
from apache_rewrite_tester.utils import compare


__author__ = 'jwilner'


class VirtualHost(RequestHandler, ContextDirective):
    START_REGEX = re.compile(r"""
                             <VirtualHost\s+
                             (?P<ip>.+?)
                             # since IPv6 addresses delimit with colons,
                             # Apache wraps them in brackets to distinguish
                             # from the colon joining the IP from the port;
                             # apply this by refusing any closing brackets
                             # within the port group.
                             (?::(?P<port>[^\]]{,5}))>
                             """, re.VERBOSE)

    END_REGEX = re.compile(r"</VirtualHost>")

    PARSERS = ("ip", IpWildcardPattern.make), \
        ("port", PortWildcardPattern.make)

    DEFAULTS = ('port', PortWildcardPattern(PortWildcardPattern.WILDCARD)),

    INNER_DIRECTIVE_TYPES = RewriteCondition, RewriteRule, ServerName, \
        RewriteEngine

    def __init__(self, ip, port, children):
        """
        :type ip: IpWildcardPattern
        :type port: PortWildcardPattern
        :type children: tuple[SingleLineDirective]
        """
        super(VirtualHost, self).__init__(children)
        self.ip = ip
        self.port = port

        # blows up if too many but use defaults
        self.server_name, = [directive for directive in children
                             if isinstance(directive, ServerName)] or (None,)

        self.rewrite_engine, = [directive for directive in children
                                if isinstance(directive, RewriteEngine)] \
            or (RewriteEngine.get_default(),)

    def match_request(self, ip, port, requested_hostname):
        """
        :type ip: IpWildcardPattern
        :type port: PortWildcardPattern
        :type requested_hostname: str
        :rtype: (MatchType, MatchType)
        """
        ip_match = compare(self.ip, ip, wildcard=IpWildcardPattern.WILDCARD)
        port_match = \
            compare(self.port, port, wildcard=PortWildcardPattern.WILDCARD)

        ip_port_match = ip_match & port_match

        if self.server_name is None:
            return ip_port_match, None

        return ip_port_match, compare(self.server_name, requested_hostname)