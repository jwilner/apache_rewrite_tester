import unittest

from apache_rewrite_tester.rewrite_objects import VirtualHost, RewriteCondition, \
    RewriteRule
from apache_rewrite_tester.rewrite_objects.simple_directives import ServerName, \
    RewriteEngine

__author__ = 'jwilner'


class TestVirtualHost(unittest.TestCase):
    def test_parses_properly(self):
        string = """<VirtualHost *:80>
    ServerName JoeWuzHere.com
</VirtualHost>"""
        virtual_host, remainder = VirtualHost.consume(string)

        self.assertEqual("", remainder)

        self.assertEqual(VirtualHost("*", 80, (ServerName("JoeWuzHere.com"),)),
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
        expected = VirtualHost("*", 10080, directives)

        self.assertEqual(expected, virtual_host)

