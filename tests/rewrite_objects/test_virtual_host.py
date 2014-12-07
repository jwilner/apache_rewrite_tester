import unittest

from apache_rewrite_tester.rewrite_objects import VirtualHost
from apache_rewrite_tester.rewrite_objects.simple_directives import ServerName

__author__ = 'jwilner'


class TestVirtualHost(unittest.TestCase):
    def test_parses_properly(self):
        string = """<VirtualHost *:80>
    ServerName JoeWuzHere.com
</VirtualHost>"""
        virtual_host, remainder = VirtualHost.consume(string)

        self.assertEqual("", remainder)

        self.assertIsInstance(virtual_host, VirtualHost)

        self.assertEqual(80, virtual_host.port)
        self.assertEqual("*", virtual_host.ip)

        self.assertIsInstance(virtual_host.server_name, ServerName)
        self.assertEqual("JoeWuzHere.com", virtual_host.server_name)
