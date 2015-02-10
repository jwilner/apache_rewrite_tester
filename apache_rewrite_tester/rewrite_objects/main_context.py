import re

from apache_rewrite_tester.rewrite_objects import VirtualHost, \
    RewriteCondition, RewriteRule
from apache_rewrite_tester.rewrite_objects.context import ContextDirective, \
    RequestHandler
from apache_rewrite_tester.rewrite_objects.simple_directives import \
    RewriteEngine, ServerName
from apache_rewrite_tester.utils import MatchType, compare


__author__ = 'jwilner'


class MainContext(ContextDirective, RequestHandler):
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

        # the last server name defined in the main context is used.
        self.server_name = next((directive for directive in reversed(children)
                                 if isinstance(directive, ServerName)),
                                None)

        if self.server_name is None:
            raise ValueError("Backwards ip lookup or whatever not supported.")

        # self.name_virtual_hosts = {directive for directive in children
        #                            if isinstance(directive, NameVirtualHost)}

    def find_host(self, ip, port, requested_hostname):
        """
        :type ip: IpWildcardPattern
        :type port: PortWildcardPattern
        :type requested_hostname: str
        :rtype: ContextDirective
        """
        default_name_match = compare(requested_hostname, self.server_name)

        virtual_hosts = tuple(directive for directive in self.children
                              if isinstance(directive, VirtualHost))

        if not virtual_hosts:
            return self

        matches = (v_host.match_request(ip, port, requested_hostname)
                   for v_host in virtual_hosts)

        ip_port_matches, name_matches = zip(*matches)

        safe_name_matches = [(name_match if name_match is not None
                              else default_name_match)
                             for name_match in name_matches]

        rankings = zip(ip_port_matches, safe_name_matches)

        # sort by rankings
        ranked_hosts = sorted(zip(virtual_hosts, rankings), key=lambda k: k[1],
                              reverse=True)

        # only hosts that matched on IP and port at all are acceptable
        filtered_hosts = (host for host, (ip_port_match, _) in ranked_hosts
                          if ip_port_match > MatchType.NONE)

        return next(filtered_hosts, self)

    def handle_request(self, request, environment):
        """
        Given a request, return a rewritten url.

        :type request: HTTPRequest
        :type environment: MutableMapping
        :rtype: str
        """
        path = request.path
