
__author__ = 'jwilner'


class _StringConsumer(object):
    @classmethod
    def consume(cls, string):
        """
        :type string: str
        :rtype: (_StringConsumer, str)
        """
        raise NotImplementedError()


class _Parser(object):
    DEFAULTS = ()
    PARSERS = ()

    @classmethod
    def _parse(cls, match):
        """
        Goes from a regex match to a dict of strings point to appropriate types.
        Intended to be consumed by the class's constructor.

        :type match: __Regex
        :rtype: dict[str, object]
        """
        parsers = dict(cls.PARSERS)
        defaults = dict(cls.DEFAULTS)

        parsed = {}
        for name, value in match.groupdict().items():
            if value is None:  # i.e. optional regex group
                parsed[name] = defaults.get(name)
                continue

            parser = parsers.get(name, str)  # leave a string by default
            parsed_value = parser(value)

            if parsed_value is None:
                raise ValueError("Could not parse.", name, value, parser)

            parsed[name] = parsed_value

        return parsed


class RewriteObject(_Parser):
    REGEX = None

    @classmethod
    def parse(cls, string):
        """
        :type string: str
        :rtype: SingleLineDirective
        """
        match = cls.REGEX.match(string)
        if match is None:
            return None

        return cls(**cls._parse(match))


class SingleLineDirective(RewriteObject, _StringConsumer):
    @classmethod
    def consume(cls, string):
        """
        :type string: str
        :rtype: (SingleLineDirective, str)
        """
        match = cls.REGEX.match(string)
        if match is None:
            return None, string

        remainder = string[match.end():]
        return cls(**cls._parse(match)), remainder


class ContextDirective(_Parser, _StringConsumer):
    START_REGEX = None
    END_REGEX = None

    INNER_DIRECTIVE_TYPES = ()

    @classmethod
    def consume(cls, string):
        """
        :type string: str
        :rtype: (ContextDirective, str)
        """
        (start_match, end_match), children, string = cls._consume(string)
        if start_match is None:
            return None, string

        return cls(children=children, **cls._parse(start_match)), string

    @classmethod
    def _consume(cls, string):
        """
        :type string: str
        :rtype: ((__Regex, __Regex), tuple[_Parser], str)
        """
        start_match = cls.START_REGEX.match(string)
        if start_match is None:
            return (None, None), None, string

        string = string[start_match.end():]

        directives = []
        end_match = cls.END_REGEX.match(string)
        while end_match is None:
            # starting whitespace will never be significant
            string = string.lstrip()
            if not string:
                raise ValueError("Unterminated context directive")

            for inner_directive_type in cls.INNER_DIRECTIVE_TYPES:
                parsed, string = inner_directive_type.consume(string)
                if parsed is not None:
                    directives.append(parsed)
                    break
            else:
                string = string[1:]  # always advance

            end_match = cls.END_REGEX.match(string)

        return (start_match, end_match), tuple(directives), \
            string[end_match.end():]

    def __init__(self, children):
        """
        :type children: tuple[_Parser]
        """
        self.children = children
