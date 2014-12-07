import re

from apache_rewrite_tester.rewrite_objects.condition import RewriteCondition
from apache_rewrite_tester.rewrite_objects.simple_directives import \
    RewriteEngine, ServerName
from apache_rewrite_tester.rewrite_objects.rule import RewriteRule
from apache_rewrite_tester.rewrite_objects.virtual_host import VirtualHost
from apache_rewrite_tester.rewrite_objects.object import ContextDirective

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



