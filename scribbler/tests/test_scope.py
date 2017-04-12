#!/usr/bin/env python3

from unittest import TestCase

from parse import (
    Sentence,
    )
from scope import (
    Definition,
    Scope,
    )
from tokenization import (
    FirstToken,
    PeriodToken,
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
        scope.print_definitions()
        scope.print_tree()
        self.assertIs(test_def, scope.match_sentence(to_match))
