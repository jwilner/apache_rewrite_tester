import re

__author__ = 'jwilner'

INCLUDE_REGEX = re.compile(r"""^\s*Include(?P<optional>Optional)?\s+
                           (?P<include_file>\S+)\s*$""",
                           re.VERBOSE | re.IGNORECASE)


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
        elif optional:  # line is dropped
            continue
        else:
            raise KeyError(filename)

