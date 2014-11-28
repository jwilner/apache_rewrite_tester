import collections

__author__ = 'jwilner'


class RewriteObject(object):
    REGEX = None
    PARSERS = ()

    @classmethod
    def parse(cls, string):
        """
        :type string: str
        :rtype: RewriteObject
        """
        parsed = cls._parse(string)
        if parsed is None:
            return None

        return cls(**parsed)

    @classmethod
    def _parse(cls, string):
        """
        :type string: str
        :rtype: dict
        """
        match = cls.REGEX.match(string)
        if match is None:
            return None

        # keep them strings if no parser
        parsers = collections.defaultdict(str)
        parsers.update(dict(cls.PARSERS))

        parsed = {}
        for name, value in match.groupdict().items():
            parser = parsers[name]
            parsed_value = parser(value)

            if parsed_value is None:
                raise ValueError("Could not parse.", name, value, parser)

            parsed[name] = parsed_value

        return cls(**parsed)