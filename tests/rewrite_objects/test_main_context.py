import unittest

from apache_rewrite_tester.rewrite_objects.main_context import MainContext
from apache_rewrite_tester.rewrite_objects import VirtualHost
from apache_rewrite_tester.rewrite_objects.simple_directives import ServerName
from apache_rewrite_tester.rewrite_objects.ip_and_port import \
    IpWildcardPattern, PortWildcardPattern

__author__ = 'jwilner'

DEFAULT_SERVER_NAME = ServerName("joe.wuznt.here")


class TestMainContextParsing(unittest.TestCase):
    def test_consumes_properly(self):
        string = """ServerName joe.wuznt.here
<VirtualHost *:80>
    ServerName JoeWuzHere.com
</VirtualHost>"""
        main_context, remainder = MainContext.consume(string)

        self.assertEqual("", remainder)
        expected = MainContext((DEFAULT_SERVER_NAME,
                                VirtualHost(IpWildcardPattern("*"),
                                            PortWildcardPattern(80),
                                            (ServerName("JoeWuzHere.com"),))))

        self.assertEqual(expected, main_context)

    def test_consumes_multiple(self):
        string = """ServerName howza
<VirtualHost *:80>
    ServerName JoeWuzHere.com
</VirtualHost>"""
        main_context, remainder = MainContext.consume(string)
        self.assertEqual("", remainder)

        server_name, remainder = ServerName.consume(string)
        virtual_host, remainder = VirtualHost.consume(remainder)
        expected = MainContext((server_name, virtual_host))
        self.assertEqual(expected, main_context)


class TestFindHost(unittest.TestCase):
    def test_returns_self(self):
        mc = MainContext((DEFAULT_SERVER_NAME,))
        self.assertIs(mc, mc.find_host(IpWildcardPattern('blha.blah'),
                                       PortWildcardPattern(92),
                                       'blah.com'))

    def test_returns_first_of_a_tie(self):
        a = VirtualHost(IpWildcardPattern('bob.bob'), PortWildcardPattern(92),
                        ())
        b = VirtualHost(IpWildcardPattern('bob.bob'), PortWildcardPattern(92),
                        ())
        context = MainContext((DEFAULT_SERVER_NAME, a, b))

        result = context.find_host(IpWildcardPattern('bob.bob'),
                                   PortWildcardPattern(92), 'some_shit')
        self.assertIs(a, result)

    def test_prefers_no_wildcards(self):
        a = VirtualHost(IpWildcardPattern(IpWildcardPattern.WILDCARD),
                        PortWildcardPattern(80), ())
        b = VirtualHost(IpWildcardPattern('bob.bob'), PortWildcardPattern(80),
                        ())
        result = MainContext((DEFAULT_SERVER_NAME, a, b))\
            .find_host(IpWildcardPattern('bob.bob'), PortWildcardPattern(80),
                       'some_shit')
        self.assertIs(b, result)

    def test_tries_server_name_to_break_tie(self):
        a = VirtualHost(IpWildcardPattern(IpWildcardPattern.WILDCARD),
                        PortWildcardPattern(80), (ServerName('not.a.match'),))
        b = VirtualHost(IpWildcardPattern(IpWildcardPattern.WILDCARD),
                        PortWildcardPattern(80), (ServerName('a.match'),))
        result = MainContext((DEFAULT_SERVER_NAME, a, b))\
            .find_host(IpWildcardPattern('bob.bob'), PortWildcardPattern(80),
                       'a.match')
        self.assertIs(b, result)

    def disregards_complete_non_matches(self):
        a = VirtualHost(IpWildcardPattern("china"), PortWildcardPattern(80),
                        (ServerName('japan'),))
        b = VirtualHost(IpWildcardPattern(IpWildcardPattern.WILDCARD),
                        PortWildcardPattern(80), (ServerName('a.match'),))
        result = MainContext((DEFAULT_SERVER_NAME, a, b))\
            .find_host(IpWildcardPattern('bob.bob'), PortWildcardPattern(80),
                       'something-else')
        self.assertIs(b, result)

