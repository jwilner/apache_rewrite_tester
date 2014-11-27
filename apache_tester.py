import re


class RewriteObject(object):
    REGEX = None

    @classmethod
    def make(cls, string):
        """
        :type string: str
        :rtype: RewriteObject
        """
        match = RewriteObject.REGEX.match(string)
        if match is None:
            return None
        return cls(**match.groupdict())


class RewriteRule(RewriteObject):
    REGEX = re.compile(r"""
                       ^RewriteRule\s+
                       (?P<pattern>\S+)\s+
                       (?P<substitution>\S+)\s+
                       (?P<flags>\S+)$
                       """, re.VERBOSE)

    def __init__(self, pattern, substitution, flags):
        """
        :type pattern: str
        :type substitution: str
        :type flags: str
        """
        self.matcher = pattern
        self.rewrite = substitution
        self.flags = flags


class RewriteCondition(RewriteObject):
    REGEX = re.compile(r"""
                       ^RewriteCond\s+
                       %\{(?P<test_string>\w+)\}\s+
                       (?P<cond_pattern>\S+)$
                       """, re.VERBOSE)

    def __init__(self, test_string, cond_pattern):
        """
        :type test_string: str
        :type cond_pattern: str
        """
        self.test_string = test_string
        self.condition = cond_pattern


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
            rewrite_cond = RewriteCondition.make(line)
            if rewrite_cond is None:
                parsed_rule = RewriteRule.make(line)
                if parsed_rule is None:
                    continue
                yield tuple(block), parsed_rule
                block = []
            else:
                block.append(rewrite_cond)
