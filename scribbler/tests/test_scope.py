#!/usr/bin/env python3

from contextlib import contextmanager
from unittest import TestCase

from parse import (
    Sentence,
    string_to_signature,
    )
from scope import (
    Definition,
    Scope,
    )
from tokenization import (
    FirstToken,
    PeriodToken,
    tokenify,
    WordToken,
    )


class TestScope(TestCase):

    def test_scope_parent(self):
        Scope(Scope(None))
        with self.assertRaises(TypeError):
            Scope(False)

    def test_match_sentence(self):
        pattern = [FirstToken('Test'), WordToken('value')]
        to_match = Sentence(pattern + [PeriodToken()])
        code = None
        test_def = Definition(pattern, code)
        scope = Scope(None)
        scope.add_definition(test_def)
        #scope.print_definitions()
        #scope.print_tree()
        self.assertIs(test_def, scope.match_sentence(to_match))


def make_test_scopes():
    scope0 = Scope(None)
    scope0.add_definition(Definition(
        string_to_signature('Fake sentence for testing.'), 0))
    scope0.add_definition(Definition(
        string_to_signature('Beginning Middle. end.'), 1))
    return [scope0, Scope(scope0)]


class TestScopeMatcher(TestCase):

    def test_matcher_match_simple(self):
        matcher = make_test_scopes()[0].new_matcher()
        self.assertTrue(matcher.next(tokenify('Fake')))
        self.assertTrue(matcher.next(tokenify('sentence')))
        self.assertIsNone(matcher.has_end())
        self.assertTrue(matcher.next(tokenify('for')))
        self.assertTrue(matcher.next(tokenify('testing')))
        self.assertIsInstance(matcher.has_end(), Definition)
        self.assertEqual(matcher.has_end().code, 0)
        self.assertFalse(matcher.next(tokenify('.')))

    def test_matcher_match_nested(self):
        matcher = make_test_scopes()[0].new_matcher()
        self.assertTrue(matcher.next(tokenify('Beginning')))
        self.assertFalse(matcher.next(tokenify('Middle')))
        self.assertTrue(matcher.next())
        self.assertTrue(matcher.next(tokenify('end')))
        self.assertIsInstance(matcher.has_end(), Definition)

    def test_matcher_no_match_sentence(self):
        matcher = make_test_scopes()[0].new_matcher()
        self.assertTrue(matcher.next(tokenify('Fake')))
        self.assertFalse(matcher.next())

    def test_matcher_parent(self):
        matcher = make_test_scopes()[1].new_matcher()
        self.assertTrue(matcher.next(tokenify('Beginning')))
        self.assertTrue(matcher.next())
        self.assertTrue(matcher.next(tokenify('end')))
        self.assertTrue(matcher.has_end())

    def test_matcher_stable_no_next(self):
        matcher = make_test_scopes()[0].new_matcher()
        self.assertTrue(matcher.next(tokenify('Fake')))
        self.assertFalse(matcher.next(tokenify('token')))
        self.assertTrue(matcher.next(tokenify('sentence')))
