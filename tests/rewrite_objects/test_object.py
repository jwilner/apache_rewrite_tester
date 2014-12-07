import unittest
import re
from apache_rewrite_tester.rewrite_objects.object import \
    RecursiveContextDirective
from apache_rewrite_tester.rewrite_objects.simple_directives import \
    ServerName, RewriteEngine

__author__ = 'jwilner'


class PretendContextDirective(RecursiveContextDirective):
    START_REGEX = re.compile(r"<Pretend (?P<a>\d)-(?P<b>\d)>")
    END_REGEX = re.compile(r"</Pretend>")
    INNER_DIRECTIVE_TYPES = ServerName, RewriteEngine

    PARSERS = ('a', int), ('b', int)

    def __init__(self, children, a, b):
        super(PretendContextDirective, self).__init__(children)
        self.a = a
        self.b = b


class TestContextDirectiveConsume(unittest.TestCase):
    def test_unnested(self):
        string = """<Pretend 1-2>
ServerName JoeWuzHere
RewriteEngine on
</Pretend>"""
        pretend_context, remainder = PretendContextDirective.consume(string)

        self.assertEqual("", remainder)
        self.assertIsInstance(pretend_context, PretendContextDirective)

        self.assertEqual(1, pretend_context.a)
        self.assertEqual(2, pretend_context.b)

        children = pretend_context.children
        self.assertEqual(2, len(children))

        first, second = children

        self.assertIsInstance(first, ServerName)
        self.assertEqual(ServerName("JoeWuzHere"), first)

        self.assertIsInstance(second, RewriteEngine)
        self.assertTrue(second.on)

    def test_raises_value_error(self):
        string = """<Pretend 1-2>
ServerName JoeWuzHere
RewriteEngine on
"""
        self.assertRaises(ValueError, PretendContextDirective.consume, string)

    def test_nested(self):
        string = """<Pretend 1-2>
<Pretend 3-4>
ServerName JoeWuzHere
RewriteEngine on
</Pretend>
</Pretend>"""
        pretend_context, remainder = PretendContextDirective.consume(string)
        self.assertEqual("", remainder)

        self.assertIsInstance(pretend_context, PretendContextDirective)
        self.assertEqual(1, pretend_context.a)
        self.assertEqual(2, pretend_context.b)

        children = pretend_context.children
        self.assertEqual(1, len(children))

        nested, = children

        self.assertIsInstance(nested, PretendContextDirective)
        self.assertEqual(3, nested.a)
        self.assertEqual(4, nested.b)

        children = nested.children
        self.assertEqual(2, len(children))

        first, second = nested.children

        self.assertIsInstance(first, ServerName)
        self.assertEqual(ServerName("JoeWuzHere"), first)

        self.assertIsInstance(second, RewriteEngine)
        self.assertTrue(second.on)

    def test_handles_empty_ok(self):
        string = """<Pretend 1-2>
<Pretend 3-4>
</Pretend>
</Pretend>"""
        pretend_context, remainder = PretendContextDirective.consume(string)
        self.assertEqual("", remainder)

        self.assertIsInstance(pretend_context, PretendContextDirective)
        self.assertEqual(1, pretend_context.a)
        self.assertEqual(2, pretend_context.b)

        children = pretend_context.children
        self.assertEqual(1, len(children))

        nested, = children

        self.assertIsInstance(nested, PretendContextDirective)
        self.assertEqual(3, nested.a)
        self.assertEqual(4, nested.b)

        self.assertSequenceEqual((), nested.children)

    def test_handles_consecutive_ok(self):
        string = """<Pretend 1-2>

</Pretend>
<Pretend 3-4>
</Pretend>
"""
        first, remainder = PretendContextDirective.consume(string)

        self.assertIsInstance(first, PretendContextDirective)
        self.assertEqual(1, first.a)
        self.assertEqual(2, first.b)

        self.assertEqual("""<Pretend 3-4>
</Pretend>
""", remainder)
