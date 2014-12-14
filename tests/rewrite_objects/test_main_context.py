import unittest

from apache_rewrite_tester.rewrite_objects.main_context import MainContext
from apache_rewrite_tester.rewrite_objects import VirtualHost
from apache_rewrite_tester.rewrite_objects.simple_directives import ServerName

__author__ = 'jwilner'


class TestMainContextParsing(unittest.TestCase):
    def test_consumes_properly(self):
        string = """<VirtualHost *:80>
    ServerName JoeWuzHere.com
</VirtualHost>"""
        main_context, remainder = MainContext.consume(string)

        self.assertEqual("", remainder)
        expected = MainContext((VirtualHost.consume(string)[0],))

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
        mc = MainContext(())
        self.assertIs(mc, mc.find_host('blha.blah', 92, 'blah.com'))

    def test_returns_first_of_a_tie(self):
        a = VirtualHost('bob.bob', 92, ())
        b = VirtualHost('bob.bob', 92, ())
        result = MainContext((a, b)).find_host('bob.bob', 92, 'some_shit')
        self.assertIs(a, result)

    def test_prefers_no_wildcards(self):
        a = VirtualHost('*', 80, ())
        b = VirtualHost('bob.bob', 80, ())
        result = MainContext((a, b)).find_host('bob.bob', 80, 'some_shit')
        self.assertIs(b, result)

    def test_tries_server_name_to_break_tie(self):
        a = VirtualHost('*', 80, (ServerName('not.a.match'),))
        b = VirtualHost('*', 80, (ServerName('a.match'),))
        result = MainContext((a, b)).find_host('bob.bob', 80, 'a.match')
        self.assertIs(b, result)

    def disregards_complete_non_matches(self):
        a = VirtualHost("china", 80, (ServerName('japan'),))
        b = VirtualHost('*', 80, (ServerName('a.match'),))
        result = MainContext((a, b)).find_host('bob.bob', 80, 'something-else')
        self.assertIs(b, result)

