import re
from apache_rewrite_tester.rewrite_objects.object import MakeableRewriteObject
from apache_rewrite_tester.utils import KeyedEqualityMixin

__author__ = 'jwilner'


IP_WILDCARDS = {'*', "__default__"}  # will replace with None


def _parse_apache_ip_string_with_wildcards(string):
    """
    :type string: str
    :rtype: str
    """
    return IpWildcardPattern.WILDCARD \
        if string in IP_WILDCARDS \
        else string.strip("[]")


def _parse_port_with_wildcards(string):
    """
    :type string: str
    :rtype: int
    """
    return int(string) if string.isdigit() else PortWildcardPattern.WILDCARD


class PortWildcardPattern(KeyedEqualityMixin, MakeableRewriteObject):
    REGEX = re.compile(r"(?P<port>\d{2,5}|\*)")

    PARSERS = ("port", _parse_port_with_wildcards),

    WILDCARD = 0

    def __init__(self, port):
        self.equality_key = self.port = port

    def __repr__(self):
        return "{0.__class__.__name__}({0.port})".format(self)


class IpWildcardPattern(KeyedEqualityMixin, MakeableRewriteObject):
    REGEX = re.compile(r"""
                       (?P<ip_address>
                       (?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|  # IPv4
                       (?:\[(?:[A-F\d]{1,4}:){7}[A-F\d]{1,4}\])|  # or IPv6
                       \*|
                       _default_  # or wildcards
                       )
                       """, re.VERBOSE)

    PARSERS = ("ip_address", _parse_apache_ip_string_with_wildcards),

    WILDCARD = "*"

    def __init__(self, ip_address):
        self.equality_key = self.ip_address = ip_address

    def __repr__(self):
        return "{0.__class__.__name__}({0.ip_address})".format(self)
