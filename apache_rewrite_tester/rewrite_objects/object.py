from apache_rewrite_tester.utils import EqualityMixin

__author__ = 'jwilner'


class RewriteObject(EqualityMixin):
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
    @staticmethod
    def _get_remainder(string, index):
        """
        We want to drop leading whitespace whenever possible.

        :type string: str
        :type index: int
        :rtype: str
        """
        return string[index:].lstrip()

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

        return cls(**cls._parse(match)), cls._get_remainder(string, match.end())


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


class RecursiveContextDirective(ContextDirective):
    @classmethod
    def _get_inner_directive_types(cls):
        return cls.INNER_DIRECTIVE_TYPES + (cls,)