import collections
import re

import enum

__author__ = 'jwilner'


def _make_header_value_extractor(header_key):
    """
    :type header_key: str
    :rtype: (HTTPRequest) -> str
    """
    def extract_value(request):
        """
        :type request: HTTPRequest
        :rtype: str
        """
        return request.headers[header_key]

    return extract_value


class Backreference(collections.Hashable):
    MAXIMUM_INDEX = 10  # exclusive

    @classmethod
    def from_string(cls, string):
        """
        :type string: str
        :rtype: Backreference
        """
        return cls(int(string))

    @classmethod
    def update_environment(cls, match, environment):
        """
        :type match: __Match
        :type environment: MutableMapping
        """
        for index in range(cls.MAXIMUM_INDEX):
            backreference = cls(index)
            try:
                group = match.group(index)
                environment[backreference] = group
            except IndexError:
                # unset old backreferences
                try:
                    del environment[backreference]
                except KeyError:
                    # won't be any for higher indices
                    break

    def __init__(self, index):
        """
        :type index: int
        """
        self.index = index

    def __hash__(self):
        """
        :rtype: int
        """
        return int(hash(type(self)) / (hash(self.index) or 1))

    def __eq__(self, other):
        """
        :type other: object
        :rtype: bool
        """
        return type(other) is self.__class__ and other.index == self.index


class CondBackreference(Backreference):
    pass


class RuleBackreference(Backreference):
    pass


class MapExpansion(collections.Hashable):
    REGEX = re.compile(r"""
                       ^(?P<map_name>\w+):
                       (?P<lookup_key>\w+)
                       (?:\|(?P<default>\w+))$
                       """, re.VERBOSE)

    @classmethod
    def from_string(cls, string):
        match = cls.REGEX.match(string)
        if match is None:
            return None

        return cls(**match.groupdict())

    def __init__(self, map_name, lookup_key, default):
        """
        :type map_name: str
        :type lookup_key: str
        :type default: str
        """
        self.map_name = map_name
        self.lookup_key = lookup_key
        self.default = default

    def __hash__(self):
        return hash(self.map_name + self.lookup_key)


class ServerVariableType(enum.Enum):
    HTTP_HEADERS = 0
    CONNECTION_AND_REQUEST = 1
    SERVER_INTERNALS = 2
    DATE_AND_TIME = 3
    SPECIALS = 4


class ServerVariable(enum.Enum):
    HTTP_ACCEPT = 0, ServerVariableType.HTTP_HEADERS, \
        _make_header_value_extractor("Accept")
    HTTP_COOKIE = 1, ServerVariableType.HTTP_HEADERS, \
        _make_header_value_extractor("Cookie")
    HTTP_FORWARDED = 2, ServerVariableType.HTTP_HEADERS
    HTTP_HOST = 3, ServerVariableType.HTTP_HEADERS, \
        _make_header_value_extractor("Host")
    HTTP_PROXY_CONNECTION = 4, ServerVariableType.HTTP_HEADERS, \
        _make_header_value_extractor("Proxy-Connection")
    HTTP_REFERER = 5, ServerVariableType.HTTP_HEADERS, \
        _make_header_value_extractor("Referer")
    HTTP_USER_AGENT = 6, ServerVariableType.HTTP_HEADERS, \
        _make_header_value_extractor("User-String")

    AUTH_TYPE = 7, ServerVariableType.CONNECTION_AND_REQUEST
    CONN_REMOTE_ADDR = 8, ServerVariableType.CONNECTION_AND_REQUEST
    CONTEXT_PREFIX = 9, ServerVariableType.CONNECTION_AND_REQUEST
    CONTEXT_DOCUMENT_ROOT = 10, ServerVariableType.CONNECTION_AND_REQUEST
    IPV6 = 11, ServerVariableType.CONNECTION_AND_REQUEST
    PATH_INFO = 12, ServerVariableType.CONNECTION_AND_REQUEST
    QUERY_STRING = 13, ServerVariableType.CONNECTION_AND_REQUEST
    REMOTE_ADDR = 14, ServerVariableType.CONNECTION_AND_REQUEST
    REMOTE_HOST = 15, ServerVariableType.CONNECTION_AND_REQUEST
    REMOTE_IDENT = 16, ServerVariableType.CONNECTION_AND_REQUEST
    REMOTE_PORT = 17, ServerVariableType.CONNECTION_AND_REQUEST
    REMOTE_USER = 18, ServerVariableType.CONNECTION_AND_REQUEST
    REQUEST_METHOD = 19, ServerVariableType.CONNECTION_AND_REQUEST
    SCRIPT_FILENAME = 20, ServerVariableType.CONNECTION_AND_REQUEST

    DOCUMENT_ROOT = 21, ServerVariableType.SERVER_INTERNALS
    SCRIPT_GROUP = 22, ServerVariableType.SERVER_INTERNALS
    SCRIPT_USER = 23, ServerVariableType.SERVER_INTERNALS
    SERVER_ADDR = 24, ServerVariableType.SERVER_INTERNALS
    SERVER_ADMIN = 25, ServerVariableType.SERVER_INTERNALS
    SERVER_NAME = 26, ServerVariableType.SERVER_INTERNALS
    SERVER_PORT = 27, ServerVariableType.SERVER_INTERNALS
    SERVER_PROTOCOL = 28, ServerVariableType.SERVER_INTERNALS
    SERVER_SOFTWARE = 29, ServerVariableType.SERVER_INTERNALS

    TIME_YEAR = 30, ServerVariableType.DATE_AND_TIME
    TIME_MON = 31, ServerVariableType.DATE_AND_TIME
    TIME_DAY = 32, ServerVariableType.DATE_AND_TIME
    TIME_HOUR = 33, ServerVariableType.DATE_AND_TIME
    TIME_MIN = 34, ServerVariableType.DATE_AND_TIME
    TIME_SEC = 35, ServerVariableType.DATE_AND_TIME
    TIME_WDAY = 36, ServerVariableType.DATE_AND_TIME
    TIME = 37, ServerVariableType.DATE_AND_TIME

    API_VERSION = 38, ServerVariableType.SPECIALS
    HTTPS = 39, ServerVariableType.SPECIALS
    IS_SUBREQ = 40, ServerVariableType.SPECIALS
    REQUEST_FILENAME = 41, ServerVariableType.SPECIALS
    REQUEST_SCHEME = 42, ServerVariableType.SPECIALS
    REQUEST_URI = 43, ServerVariableType.SPECIALS
    THE_REQUEST = 44, ServerVariableType.SPECIALS

    def __init__(self, index, variable_type, extractor=None):
        """
        :type index: int
        :type variable_type: ServerVariableType
        """
        self.id = index
        self.type = variable_type
        self.extract = extractor


class ApacheFlag(enum.Enum):
    def __init__(self, pattern, parsers=()):
        """
        :type pattern: str
        """
        self.pattern = re.compile(pattern, re.IGNORECASE | re.VERBOSE)
        self.parsers = parsers

    @classmethod
    def look_up(cls, string):
        """
        :type string: str
        :rtype: ApacheFlag, dict
        """
        for flag in cls:
            match = flag.pattern.match(string)
            if match is not None:
                parsers = dict(flag.parsers)

                arguments = {}
                for key, value in match.groupdict().items():
                    if value is None:
                        continue
                    parser = parsers.get(key, str)
                    arguments[key] = parser(value)

                return flag, arguments

        raise ValueError("{} is not a valid {}".format(string, cls.__name__))

    @classmethod
    def find_all(cls, string):
        """
        :type string: str
        :rtype: dict[ApacheFlag, dict]
        """
        # drops empty strings
        return {flag: arguments for flag, arguments in
                map(cls.look_up, filter(bool, string.split(',')))}



class Environment(collections.MutableMapping):
    def __getitem__(self, key):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

