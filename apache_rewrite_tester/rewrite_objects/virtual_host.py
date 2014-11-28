import re

from apache_rewrite_tester.rewrite_objects.object import RewriteObject
from apache_rewrite_tester.rewrite_objects.condition import \
    RewriteCondition
from apache_rewrite_tester.rewrite_objects.rule import RewriteRule

__author__ = 'jwilner'


class VirtualHost(RewriteObject):
    REGEX = re.compile(r"""
                       <VirtualHost\s+\*:(?P<port>\d{1,5})>
                       (?P<body>.+)
                       </VirtualHost>
                       """, re.VERBOSE | re.DOTALL)
    SERVER_NAME_REGEX = re.compile(r'ServerName\s+(\S+)')

    def __init__(self, port, body):
        """
        :type port: str
        :type body: str
        """
        self.port = port

        server_name = self.SERVER_NAME_REGEX.search(body)
        if server_name is None:
            raise RuntimeError()

        self.server_name = server_name.group(1)

        self.rewrite_blocks = tuple(self._find_rewrite_blocks(body))

    @classmethod
    def _find_rewrite_blocks(cls, body):
        """
        :type body: str
        :rtype: list
        """
        lines = map(str.strip, body.split('\n'))
        block = []

        for line in lines:
            rewrite_cond = RewriteCondition.parse(line)
            if rewrite_cond is None:
                parsed_rule = RewriteRule.parse(line)
                if parsed_rule is None:
                    continue
                yield tuple(block), parsed_rule
                block = []
            else:
                block.append(rewrite_cond)