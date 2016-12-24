#!/usr/bin/env python3

from unittest import TestCase

from scope import (
    Scope,
    )


class TestScope(TestCase):

    def test_scope_parent(self):
        Scope(Scope(None))
        with self.assertRaises(TypeError):
            Scope(False)
