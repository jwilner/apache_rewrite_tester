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


