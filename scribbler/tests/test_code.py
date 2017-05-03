#!/usr/bin/env python3
"""Tests for built in code."""


from code import (
    create_built_in_scope,
    define_function,
    )
from parse import (
    string_to_signature,
    )
from scope import (
    Scope,
    )
from sentence import (
    Sentence,
    )
from tokenization import (
    FirstToken,
    WordToken,
    )
from unittest import TestCase


class TestDefineFunction(TestCase):

    def test_define_identity(self):
        action = define_function(Scope(),
            string_to_signature('Identity Id. .'),
            string_to_signature('Id.'))
        self.assertIsNone(action.definition.code(Scope(), None))


class TestCreateBuiltInScope(TestCase):

    def test_has_define_function(self):
        scope = create_built_in_scope()
        ptr = scope.new_matcher()
        ptr.next(FirstToken('Define'))
        ptr.next()
        ptr.next(WordToken('to'))
        ptr.next(WordToken('be'))
        ptr.next()
        self.assertTrue(ptr.has_end())
