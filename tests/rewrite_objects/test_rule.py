import unittest

from apache_rewrite_tester.environment import RuleBackreference
from apache_rewrite_tester.rewrite_objects.rule import RuleFlag, RewriteRule

__author__ = 'jwilner'


CASES = (RuleFlag.ESCAPE_BACKREFERENCES, "B"), (RuleFlag.CHAIN, "C"), \
    (RuleFlag.CHAIN, "chaiN"), \
    (RuleFlag.COOKIE, "CO=frontdoor:yes:.example.com:1440:/",
     {"name": "frontdoor", "value": "yes", "domain": ".example.com",
      "lifetime": 1440, "path": "/"}), \
    (RuleFlag.COOKIE, "CO=frontdoor:yes:.example.com:1440:/:yes:yes",
     {"name": "frontdoor", "value": "yes", "domain": ".example.com",
      "lifetime": 1440, "path": "/", "secure": "yes", "httponly": "yes"}), \
    (RuleFlag.COOKIE, "CO=frontdoor:yes:.example.com",
     {"name": "frontdoor", "value": "yes", "domain": ".example.com"}), \
    (RuleFlag.DISCARD_PATH_INFO, "DPi"), \
    (RuleFlag.DISCARD_PATH_INFO, "DiscardPATH"), \
    (RuleFlag.ENVIRONMENT_VARIABLE, "E=bob:a",
     {"variable": "bob", "value": "a"}), \
    (RuleFlag.ENVIRONMENT_VARIABLE, "E=!bob", {"variable_to_unset": "bob"}), \
    (RuleFlag.END, "END"), (RuleFlag.FORBIDDEN, "f"), \
    (RuleFlag.FORBIDDEN, "FORBIDDEN"), (RuleFlag.GONE, "g"), \
    (RuleFlag.GONE, "GoNe"), (RuleFlag.HANDLER, "H=application/x-httpd-php",
                              {"handler": "application/x-httpd-php"}), \
    (RuleFlag.LAST, "l"), (RuleFlag.LAST, "lasT"), (RuleFlag.NEXT, "NeXT"), \
    (RuleFlag.NEXT, "N=42", {"maximum": 42}), (RuleFlag.NO_CASE, "NC"), \
    (RuleFlag.NO_CASE, "noCASE"), (RuleFlag.NO_ESCAPE, "NE"), \
    (RuleFlag.NO_ESCAPE, "noEsCAPE"), (RuleFlag.NO_SUBREQUEST, "NS"), \
    (RuleFlag.NO_SUBREQUEST, "nosubreq"), (RuleFlag.PROXY, "P"), \
    (RuleFlag.PROXY, "proXY"), (RuleFlag.PASS_THROUGH, "pt"), \
    (RuleFlag.PASS_THROUGH, "passThrouGH"), \
    (RuleFlag.QUERY_STRING_APPEND,  "qsappend"), \
    (RuleFlag.QUERY_STRING_APPEND, "QSA"), \
    (RuleFlag.QUERY_STRING_DISCARD, "qsd"), \
    (RuleFlag.QUERY_STRING_DISCARD, "qsDISCARD"), \
    (RuleFlag.REDIRECT, "r=301", {"status_code": 301}), \
    (RuleFlag.REDIRECT, "rEDIRECT=silly", {"status_name": "silly"}),\
    (RuleFlag.SKIP, "s=1", {"number": 1}), \
    (RuleFlag.SKIP, "skip=10", {"number": 10}), \
    (RuleFlag.TYPE, "t=bob/bob", {"content_type": "bob/bob"}), \
    (RuleFlag.TYPE, "type=bob", {"content_type": "bob"}),


class TestRewriteRuleFlagParsing(unittest.TestCase):
    CASES = tuple((case if len(case) == 3 else case + ({},))
                  for case in CASES)

    def test_rewrite_rule_flags(self):
        for expected_flag, string, expected_arguments in self.CASES:
            flag, arguments = RuleFlag.look_up(string)
            self.assertIs(expected_flag, flag)
            self.assertEqual(expected_arguments, arguments)

    def test_find_all(self):
        strung = "b,CO=frontdoor:yes:.example.com:1440:/:yes:yes,T=bob"
        result = RuleFlag.find_all(strung)
        expected = {RuleFlag.ESCAPE_BACKREFERENCES: {},
                    RuleFlag.TYPE: {"content_type": "bob"},
                    RuleFlag.COOKIE: {"name": "frontdoor", "value": "yes",
                                      "domain": ".example.com",
                                      "lifetime": 1440, "path": "/",
                                      "secure": "yes", "httponly": "yes"}}
        self.assertDictEqual(expected, result)


class TestRewriteRule(unittest.TestCase):
    def test_basic_parsing(self):
        string = "RewriteRule ^/somepath(.*) /otherpath$1"
        parsed = RewriteRule.parse(string)

        self.assertIsNotNone(parsed)

        self.assertFalse(parsed.pattern.negated)
        self.assertEqual("^/somepath(.*)", parsed.pattern.pattern)

        expected_components = tuple("/otherpath") + (RuleBackreference(1),)

        self.assertSequenceEqual(expected_components,
                                 parsed.substitution.components)

        self.assertDictEqual({}, parsed.flags)

    def test_parsing_with_flag(self):
        string = "RewriteRule !^/somepath(.*) http://thishost/otherpath$1 [P]"
        parsed = RewriteRule.parse(string)

        self.assertIsNotNone(parsed)

        self.assertTrue(parsed.pattern.negated)
        self.assertEqual("^/somepath(.*)", parsed.pattern.pattern)

        expected_components = tuple("http://thishost/otherpath") + \
            (RuleBackreference(1),)

        self.assertSequenceEqual(expected_components,
                                 parsed.substitution.components)

        self.assertDictEqual({RuleFlag.PROXY: {}}, parsed.flags)
