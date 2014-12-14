import re

from apache_rewrite_tester.rewrite_objects.condition import RewriteCondition
from apache_rewrite_tester.rewrite_objects.object import RewriteObject, \
    Directive
from apache_rewrite_tester.rewrite_objects.simple_directives import \
    RewriteEngine, ServerName
from apache_rewrite_tester.rewrite_objects.rule import RewriteRule
from apache_rewrite_tester.rewrite_objects.virtual_host import VirtualHost

__author__ = 'jwilner'


class ContextDirective(RewriteObject, Directive):
    START_REGEX = None
    END_REGEX = None

    INNER_DIRECTIVE_TYPES = ()

    @classmethod
    def consume(cls, string):
        """
        :type string: str
        :rtype: (ContextDirective, str)
        """
        (start_match, end_match), children, string = \
            cls._consume(string, cls._get_inner_directive_types())
        if start_match is None:
            return None, string

        kwargs = cls._parse(start_match)
        kwargs.update(cls._parse(end_match))

        return cls(children=children, **kwargs), string

    @classmethod
    def _get_inner_directive_types(cls):
        return cls.INNER_DIRECTIVE_TYPES

    @classmethod
    def _consume(cls, string, inner_directive_types):
        """
        Get delimiting matches and the internal directives from a string

        :type string: str
        :rtype: ((__Match, __Match), tuple[Directive], str)
        """
        start_match = cls.START_REGEX.match(string)
        if start_match is None:
            return (None, None), None, string

        string = cls._get_remainder(string, start_match.end())

        directives = []
        end_match = cls.END_REGEX.match(string)
        while end_match is None:
            if not string:
                raise ValueError("Unterminated context directive")

            for inner_directive_type in inner_directive_types:
                directive, string = inner_directive_type.consume(string)
                if directive is not None:
                    directives.append(directive)
                    break
            else:
                # always advance, and starting whitespace will never be
                # significant so lop it off if present
                string = string[1:].lstrip()

            end_match = cls.END_REGEX.match(string)

        return (start_match, end_match), tuple(directives), \
            string[end_match.end():]

    def __init__(self, children):
        """
        :type children: tuple[Directive]
        """
        self.children = children


class MainContext(ContextDirective):
    INNER_DIRECTIVE_TYPES = VirtualHost, RewriteCondition, RewriteRule, \
        RewriteEngine, ServerName

    # we want this to consume the whole string
    START_REGEX = re.compile(r'^')
    END_REGEX = re.compile(r'$')

    def __init__(self, children):
        """
        :type children: tuple[Directive]
        """
        super(MainContext, self).__init__(children)

        server_names = [directive for directive in children
                        if isinstance(directive, ServerName)] or [None]
        # the last defined server name is used.
        self.server_name = server_names[-1]

    def find_host(self, ip, port, requested_hostname):
        """
        :type ip: str
        :type port: int|str
        :type requested_hostname: str
        :rtype: ContextDirective
        """
        virtual_hosts = tuple(directive for directive in self.children
                              if isinstance(directive, VirtualHost))

        rankings = (v_host.match_request(ip, port, requested_hostname,
                                         self.server_name)
                    for v_host in virtual_hosts)

        # sort by rankings
        ranked_hosts = sorted(zip(virtual_hosts, rankings), key=lambda k: k[1])

        # return the best matching that matches at all for ip, else return self
        # as default
        return next((host for host, (ip_match, name_match) in ranked_hosts
                     if ip_match < VirtualHost.NO_MATCH),
                    self)


class RecursiveContextDirective(ContextDirective):
    @classmethod
    def _get_inner_directive_types(cls):
        return cls.INNER_DIRECTIVE_TYPES + (cls,)