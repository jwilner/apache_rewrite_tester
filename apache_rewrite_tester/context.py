import collections

import enum
import re

__author__ = 'jwilner'


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
    def update_context(cls, match, context):
        """
        :type match: __Match
        :type context: MutableMapping
        """
        for index in range(cls.MAXIMUM_INDEX):
            backreference = cls(index)
            try:
                group = match.group(index)
                context[backreference] = group
            except IndexError:
                # unset old backreferences
                try:
                    del context[backreference]
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
        return self.index


class CondBackreference(Backreference):
    pass


class RuleBackreference(Backreference):
    pass


class MapExpansion(collections.Hashable):
    REGEX = re.compile(r"""
                       ^(?P<map_name>\w+):
                       (?P<lookup_key>\w+)
                       (?:\|(?P<default>\w+))
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


class ServerVariableType(enum):
    HTTP_HEADERS = 0
    CONNECTION_AND_REQUEST = 1
    SEVER_INTERNALS = 2
    DATE_AND_TIME = 3
    SPECIALS = 4


class ServerVariable(enum):
    HTTP_ACCEPT = 0, ServerVariableType.HTTP_HEADERS
    HTTP_COOKIE = 1, ServerVariableType.HTTP_HEADERS
    HTTP_FORWARDED = 2, ServerVariableType.HTTP_HEADERS
    HTTP_HOST = 3, ServerVariableType.HTTP_HEADERS
    HTTP_PROXY_CONNECTION = 4, ServerVariableType.HTTP_HEADERS
    HTTP_REFERER = 5, ServerVariableType.HTTP_HEADERS
    HTTP_USER_AGENT = 6, ServerVariableType.HTTP_HEADERS

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

    DOCUMENT_ROOT = 21, ServerVariableType.SEVER_INTERNALS
    SCRIPT_GROUP = 22, ServerVariableType.SEVER_INTERNALS
    SCRIPT_USER = 23, ServerVariableType.SEVER_INTERNALS
    SERVER_ADDR = 24, ServerVariableType.SEVER_INTERNALS
    SERVER_ADMIN = 25, ServerVariableType.SEVER_INTERNALS
    SERVER_NAME = 26, ServerVariableType.SEVER_INTERNALS
    SERVER_PORT = 27, ServerVariableType.SEVER_INTERNALS
    SERVER_PROTOCOL = 28, ServerVariableType.SEVER_INTERNALS
    SERVER_SOFTWARE = 29, ServerVariableType.SEVER_INTERNALS

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

    def __init__(self, index, variable_type):
        """
        :type index: int
        :type variable_type: apache_rewrite_tester.context.ServerVariableType
        """
        self.id = index
        self.type = variable_type


class ApacheFlag(enum):
    def __init__(self, short_name, long_name):
        """
        :type short_name: str
        :type long_name: str
        """
        self.short_name = short_name
        self.long_name = long_name

    @classmethod
    def __call__(cls, string):
        """
        :type string: str
        :rtype: ApacheFlag
        """
        for flag in cls:
            if flag.short_name == string or flag.long_name == string:
                return string

        raise ValueError("{} is not a valid {}".format(string, cls.__name__))

    @classmethod
    def find_all(cls, string):
        """
        :type string: str
        :rtype: frozenset[ApacheFlag]
        """
        return frozenset(map(cls.__call__, string.split(',')))
