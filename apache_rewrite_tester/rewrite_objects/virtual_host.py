import re

from apache_rewrite_tester.rewrite_objects.object import RewriteObject
from apache_rewrite_tester.rewrite_objects.condition import \
    RewriteCondition
from apache_rewrite_tester.rewrite_objects.rule import RewriteRule

__author__ = 'jwilner'

IP_WILDCARD = '*'  # will replace _default_ with this
PORT_WILDCARD = '*'  # will replace None with this


def _parse_apache_ip_string_with_wildcards(string):
    """
    :type string: str
    :rtype: str
    """
    return IP_WILDCARD if string == "_default_" else string.strip("[]")


class VirtualHost(RewriteObject):
    REGEX = re.compile(r"""
                       <VirtualHost\s+
                       (?P<ip>
                       \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|  # IPv4
                       \[(?:[A-F\d]{1,4}:){7}[A-F\d]{1,4}\]|  # or IPv6
                       \*|_default_  # or wildcards
                       ?)
                       (?::(?P<port>\d{1,5}|\*))>
                       (?P<body>.+?)
                       </VirtualHost>
                       """, re.VERBOSE | re.DOTALL)

    # n.b. port is a string because might be a wildcard
    PARSERS = ("ip", _parse_apache_ip_string_with_wildcards), ("port", str)
    DEFAULTS = ('port', PORT_WILDCARD),

    SERVER_NAME_REGEX = re.compile(r"ServerName\s+(\S+)")

    DIRECTIVES = RewriteCondition, RewriteRule

    @classmethod
    def _parse(cls, match):
        """
        :type match: __Regex
        :rtype: dict
        """
        parsed_dict = super(VirtualHost, cls)._parse(match)
        if parsed_dict is None:
            return None

        body = parsed_dict.pop("body")

        matches = cls.SERVER_NAME_REGEX.findall(body)
        if not matches:
            return None
        parsed_dict["server_name"], = matches  # blows up if more than one

        body = cls.SERVER_NAME_REGEX.sub("", body)

        parsed_dict["directives"] = tuple(cls._parse_directives(body))
        return parsed_dict

    @classmethod
    def _parse_directives(cls, string):
        for line in map(str.strip, string.splitlines()):
            for directive in cls.DIRECTIVES:
                parsed = directive.parse(line)
                if parsed is not None:
                    yield parsed
                    break

    def __init__(self, server_name, port, directives):
        """
        :type port: int
        :type server_name: str
        :type directives: Iterable[RewriteObject]
        """
        self.server_name = server_name
        self.port = port
        self.directives = directives

    def apply(self, path, environment):
        """
        :type path: str
        :type environment: MutableMapping
        :rtype: str
        """
