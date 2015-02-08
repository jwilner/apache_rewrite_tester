import unittest

from apache_rewrite_tester.rewrite_objects import VirtualHost, \
    RewriteCondition, RewriteRule
from apache_rewrite_tester.rewrite_objects.simple_directives import \
    RewriteEngine, ServerName
from apache_rewrite_tester.rewrite_objects.ip_and_port import \
    IpWildcardPattern, PortWildcardPattern
from apache_rewrite_tester.utils import MatchType

__author__ = 'jwilner'


class TestVirtualHost(unittest.TestCase):
    def test_parses_properly(self):
        string = """<VirtualHost *:80>
    ServerName JoeWuzHere.com
</VirtualHost>"""
        virtual_host, remainder = VirtualHost.consume(string)

        self.assertEqual("", remainder)

        ip_wildcard = IpWildcardPattern(IpWildcardPattern.WILDCARD)

        self.assertEqual(VirtualHost(ip_wildcard, PortWildcardPattern(80),
                                     (ServerName("JoeWuzHere.com"),)),
                         virtual_host)

    def test_more_elaborate_parse(self):
        string = """<VirtualHost *:10080>
    ServerName JoeWuzHere.com
    RewriteEngine on
    RewriteCond  %{HTTP_USER_AGENT}  (iPhone|Blackberry|Android)
    RewriteRule  ^/$                 /homepage.mobile.html  [L]

    RewriteRule  ^/$                 /homepage.std.html  [L]
</VirtualHost>"""

        virtual_host, remainder = VirtualHost.consume(string)

        condition = RewriteCondition.make("RewriteCond %{HTTP_USER_AGENT}  "
                                          "(iPhone|Blackberry|Android)")
        rule_one = RewriteRule.make("RewriteRule  ^/$ /homepage.mobile.html "
                                    "[L]")
        rule_two = RewriteRule.make("RewriteRule ^/$ /homepage.std.html [L]")
        directives = ServerName("JoeWuzHere.com"), RewriteEngine(on=True),\
            condition, rule_one, rule_two
        expected = VirtualHost(IpWildcardPattern(IpWildcardPattern.WILDCARD),
                               PortWildcardPattern(10080), directives)

        self.assertEqual(expected, virtual_host)


class TestMatchRequest(unittest.TestCase):
    def test_gets_perfect_match(self):
        ip = IpWildcardPattern('joe.wuz.here')
        v_host = VirtualHost(ip, PortWildcardPattern(666),
                             (ServerName('joewuzhere.com'),))
        match = v_host.match_request(IpWildcardPattern('joe.wuz.here'),
                                     PortWildcardPattern(666),
                                     'joewuzhere.com')
        self.assertEqual((MatchType.STRICT,) * 2, match)

    def test_uses_default(self):
        v_host = VirtualHost(IpWildcardPattern('joe.wuz.here'),
                             PortWildcardPattern(666), ())
        match = v_host.match_request(IpWildcardPattern('joe.wuz.here'),
                                     PortWildcardPattern(666),
                                     'blahblahblah')
        self.assertEqual((MatchType.STRICT,) * 2, match)

    def test_port_wildcard_forces(self):
        v_host = VirtualHost(IpWildcardPattern('joe.wuz.here'),
                             PortWildcardPattern(PortWildcardPattern.WILDCARD),
                             (ServerName('joewuzhere.com'),))
        match = v_host.match_request(IpWildcardPattern('joe.wuz.here'),
                                     PortWildcardPattern(666), 'joewuzhere.com')
        self.assertEqual((MatchType.WILDCARD, MatchType.STRICT),
                         match)

    def test_ip_wildcard_forces(self):
        v_host = VirtualHost(IpWildcardPattern(IpWildcardPattern.WILDCARD),
                             PortWildcardPattern(666),
                             (ServerName('joewuzhere.com'),))
        match = v_host.match_request(IpWildcardPattern('joe.wuz.here'),
                                     PortWildcardPattern(666), 'joewuzhere.com')
        self.assertEqual((MatchType.WILDCARD, MatchType.STRICT),
                         match)
