
__author__ = 'jwilner'


class RewriteObject(object):
    REGEX = None
    PARSERS = ()
    DEFAULTS = ()

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

        parsers = dict(cls.PARSERS)
        defaults = dict(cls.DEFAULTS)

        parsed = {}
        for name, value in match.groupdict().items():
            if value is None:  # i.e. optional regex group
                parsed[name] = defaults.get(name)
                continue

            parser = parsers.get(name, str)  # leave a string as default
            parsed_value = parser(value)

            if parsed_value is None:
                raise ValueError("Could not parse.", name, value, parser)

            parsed[name] = parsed_value

        return parsed

