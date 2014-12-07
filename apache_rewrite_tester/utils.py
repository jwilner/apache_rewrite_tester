import re

__author__ = 'jwilner'

INCLUDE_REGEX = re.compile(r"""^\s*Include(?P<optional>Optional)?\s+
                           (?P<include_file>\S+)\s*$""",
                           re.VERBOSE | re.IGNORECASE)


class EqualityMixin(object):
    """
    http://stackoverflow.com/questions/390250/
    elegant-ways-to-support-equivalence-equality-in-python-classes
    """
    def __eq__(self, other):
        """
        Just a useful default, basically for testing.
        :type other: object
        :rtype: bool
        """
        if type(self) != type(other):
            return NotImplemented

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        :type other: object
        :rtype: bool
        """
        return not self.__eq__(other)


def join_continued_lines(string):
    """
    :type string: str
    :rtype: str
    """
    return "\n".join(_join_continued_lines(string.splitlines()))


def _join_continued_lines(lines):
    """
    :type lines: Iterable[str]
    :rtype: __generator[str]
    """
    previous = []
    for line in lines:
        if line.endswith('\\'):
            previous.append(line[:-1])
        else:
            previous.append(line)
            yield "".join(previous)
            previous = []

    if previous:
        raise ValueError("Ended on a continued line.")


def expand_includes(string, filenames_to_contents):
    """
    :type string: str
    :type filenames_to_contents: Mapping[str, str]
    :rtype: str
    """
    return '\n'.join(_expand_includes(string, filenames_to_contents))


def _expand_includes(string, filenames_to_contents):
    """
    :type string: str
    :type filenames_to_contents: Mapping[str, str]
    :rtype: __generator[str]
    """
    for line in string.splitlines():
        match = INCLUDE_REGEX.match(line)
        if match is None:  # line doesn't have any includes
            yield line
            continue

        groups = match.groupdict()
        filename = groups["include_file"]
        optional = bool(groups["optional"])

        contents = filenames_to_contents.get(filename)

        if contents is not None:
            yield from _expand_includes(contents, filenames_to_contents)
        elif not optional:  # line is dropped if optional
            raise KeyError(filename)

