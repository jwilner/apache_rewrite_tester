import re
from apache_rewrite_tester.rewrite_objects import VirtualHost, RewriteCondition, \
    RewriteRule
from apache_rewrite_tester.rewrite_objects.context import ContextDirective
from apache_rewrite_tester.rewrite_objects.simple_directives import \
    RewriteEngine, ServerName

__author__ = 'jwilner'


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
        :type port: int
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