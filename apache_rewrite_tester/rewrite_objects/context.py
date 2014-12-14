from apache_rewrite_tester.rewrite_objects.object import RewriteObject, \
    Directive

__author__ = 'jwilner'


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