from unittest import TestCase

from apache_rewrite_tester.environment import ServerVariable
from apache_rewrite_tester.rewrite_objects.condition import RewriteCondition, \
    ConditionFlag
from apache_rewrite_tester.rewrite_objects.pattern import RegexCondPattern

__author__ = 'jwilner'


class TestConditionFlag(TestCase):
    def test_parsing(self):
        result = ConditionFlag.find_all("NC,NV,OR")
        expected = {ConditionFlag.NO_CASE: {}, ConditionFlag.NO_VARY: {},
                    ConditionFlag.OR_NEXT: {}}
        self.assertDictEqual(expected, result)

    def test_parsing_no_flags(self):
        self.assertDictEqual({}, ConditionFlag.find_all(""))


class TestRewriteConditionParsing(TestCase):
    def test_match_without_fields(self):
        string = \
            "RewriteCond  %{HTTP_USER_AGENT}  !(iPhone|Blackberry|Android)"

        condition = RewriteCondition.make(string)
        self.assertIsNotNone(condition)

        self.assertSequenceEqual((ServerVariable.HTTP_USER_AGENT,),
                                 condition.test_string.components)

        self.assertIsInstance(condition.cond_pattern, RegexCondPattern)
        self.assertEqual('(iPhone|Blackberry|Android)',
                         condition.cond_pattern.pattern)

        self.assertTrue(condition.cond_pattern.negated)

        self.assertDictEqual({}, condition.flags)

    def test_match_with_flags(self):
        string = "RewriteCond %{REMOTE_HOST}  ^host1 [OR]"
        condition = RewriteCondition.make(string)
        self.assertIsNotNone(condition)
        self.assertSequenceEqual((ServerVariable.REMOTE_HOST,),
                                 condition.test_string.components)

        self.assertIsInstance(condition.cond_pattern, RegexCondPattern)
        self.assertEquals('^host1', condition.cond_pattern.pattern)
        self.assertFalse(condition.cond_pattern.negated)

        self.assertDictEqual({ConditionFlag.OR_NEXT: {}}, condition.flags)


class FakeRewriteCondition(RewriteCondition):
    def __init__(self, evaluation, flags):
        super(FakeRewriteCondition, self).__init__(None, None, flags)
        self.evaluation = evaluation
        self.was_evaluated = False

    def evaluate(self, context):
        self.was_evaluated = True
        return self.evaluation


class TestRewriteConditionChaining(TestCase):
    def test_looks_at_all_by_default_for_true(self):
        cond_1 = FakeRewriteCondition(True, {})
        cond_2 = FakeRewriteCondition(True, {})

        result = RewriteCondition.chain([cond_1, cond_2], {})

        self.assertTrue(result)
        self.assertTrue(cond_1.was_evaluated)
        self.assertTrue(cond_2.was_evaluated)

    def test_short_circuits_on_false(self):
        cond_1 = FakeRewriteCondition(False, {})
        cond_2 = FakeRewriteCondition(True, {})

        result = RewriteCondition.chain([cond_1, cond_2], {})

        self.assertFalse(result)
        self.assertTrue(cond_1.was_evaluated)
        self.assertFalse(cond_2.was_evaluated)

    def test_only_looks_at_first_for_true_with_or(self):
        cond_1 = FakeRewriteCondition(True, {ConditionFlag.OR_NEXT})
        cond_2 = FakeRewriteCondition(False, {})

        result = RewriteCondition.chain([cond_1, cond_2], {})

        self.assertTrue(result)
        self.assertTrue(cond_1.was_evaluated)
        self.assertFalse(cond_2.was_evaluated)

    def test_looks_at_both_for_first_false_with_or(self):
        cond_1 = FakeRewriteCondition(False, {ConditionFlag.OR_NEXT})
        cond_2 = FakeRewriteCondition(True, {})

        result = RewriteCondition.chain([cond_1, cond_2], {})

        self.assertTrue(result)
        self.assertTrue(cond_1.was_evaluated)
        self.assertTrue(cond_2.was_evaluated)


CASES = ("NC", ConditionFlag.NO_CASE), \
    ("nocasE", ConditionFlag.NO_CASE), \
    ("or", ConditionFlag.OR_NEXT), \
    ("ORneXT", ConditionFlag.OR_NEXT), \
    ("Nv", ConditionFlag.NO_VARY), \
    ("NoVARY", ConditionFlag.NO_VARY)


class TestConditionFlagParsing(TestCase):
    def test_individual_flags(self):
        for string, expected_flag in CASES:
            flag, arguments = ConditionFlag.look_up(string)
            self.assertIs(expected_flag, flag)
            self.assertDictEqual({}, arguments)

    def test_find_all(self):
        string = "NC,Nv,OR"
        found = set(ConditionFlag.find_all(string).keys())
        self.assertSetEqual({ConditionFlag.NO_CASE, ConditionFlag.NO_VARY,
                             ConditionFlag.OR_NEXT},
                            found)