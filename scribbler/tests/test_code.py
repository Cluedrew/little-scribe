#!/usr/bin/env python3
"""Tests for built in code."""


from code import (
    create_built_in_scope,
    define_function,
    )
from parse import (
    Sentence,
    )
from tokenization import (
    FirstToken,
    WordToken,
    )
from unittest import TestCase


class TestDefineFunction(TestCase):

    pass
    #def test_(self)


class TestCreateBuiltInScope(TestCase):

    def test_has_define_function(self):
        scope = create_built_in_scope()
        ptr = scope.new_matcher()
        ptr.next(FirstToken('Define'))
        ptr.next(None)
        ptr.next(WordToken('to'))
        ptr.next(WordToken('be'))
        ptr.next(None)
        self.assertTrue(ptr.has_end())
