
__author__ = 'jwilner'


class RewriteObject(object):
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


class Directive(object):
    @classmethod
    def consume(cls, string):
        """
        :type string: str
        :rtype: (Directive, str)
        """
        raise NotImplementedError()


class MakeableRewriteObject(RewriteObject):
    REGEX = None

    @classmethod
    def make(cls, string):
        """
        :type string: str
        :rtype: SingleLineDirective
        """
        match = cls.REGEX.match(string)
        if match is None:
            return None

        return cls(**cls._parse(match))


class SingleLineDirective(MakeableRewriteObject, Directive):
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
        (start_match, end_match), children, string = cls._consume(string)
        if start_match is None:
            return None, string

        kwargs = cls._parse(start_match)
        kwargs.update(cls._parse(end_match))

        return cls(children=children, **kwargs), string

    @classmethod
    def _consume(cls, string):
        """
        Get delimiting matches and the internal directives from a string

        :type string: str
        :rtype: ((__Match, __Match), tuple[Directive], str)
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
        :type children: tuple[Directive]
        """
        self.children = children
