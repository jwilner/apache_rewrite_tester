import unittest

__author__ = 'jwilner'

from apache_rewrite_tester.utils import expand_includes, join_continued_lines


class TestExpandIncludes(unittest.TestCase):
    def test_does_nothing(self):
        string = """How does this work?
All right?"""

        self.assertEqual(string,
                         expand_includes(string, {}))

    def test_includes_stuff(self):
        string = """Once
there
was
Include some_file"""
        include_string = """a
man"""
        expected = """Once
there
was
a
man"""

        strung = expand_includes(string,
                                 {'some_file': include_string})
        self.assertEqual(expected, strung)

    def test_optional_include_absent(self):
        string = """Once
there
was
IncludeOptional some_other_file
Include some_file"""
        include_string = """a
man"""
        expected = """Once
there
was
a
man"""
        strung = expand_includes(string,
                                 {'some_file': include_string})
        self.assertEqual(expected, strung)

    def test_optional_include_present(self):
        string = """Once
there
was
IncludeOptional some_other_file
Include some_file"""
        include_string = """a
man"""
        expected = """Once
there
was
a
man
a
man"""
        includes = {'some_file': include_string,
                    'some_other_file': include_string}

        self.assertEqual(expected,
                         expand_includes(string, includes))

    def test_nested_includes(self):
        string = """Once
there
was
Include some_file"""
        include_string = """a
man
Include some_other_file"""
        other_string = """a
man"""
        expected = """Once
there
was
a
man
a
man"""
        includes = {'some_file': include_string,
                    'some_other_file': other_string}

        self.assertEqual(expected,
                         expand_includes(string, includes))


class TestJoinContinuedLines(unittest.TestCase):
    def test_lines_are_joined(self):
        string = """some shitty \\
continuing \\
lines
are on this page"""

        expected = """some shitty continuing lines
are on this page"""

        self.assertEqual(expected, join_continued_lines(string))

    def test_invalid_raises_value_error(self):
        string = """some shitty \\"""

        self.assertRaises(ValueError, join_continued_lines, string)

    def test_leaves_stuff_alone(self):
        string = """leaves
expected
stuff

alone"""
        self.assertEqual(string, join_continued_lines(string))