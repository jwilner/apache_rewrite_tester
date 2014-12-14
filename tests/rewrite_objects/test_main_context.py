import unittest
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