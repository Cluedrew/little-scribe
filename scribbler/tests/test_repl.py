#!/usr/bin/env python3


from unittest import TestCase

from io import (
    StringIO
    )
from repl import (
    repl_core,
    )


class TestRepl(TestCase):

    def test_one_two_three(self):
        output = StringIO()
        repl_core('tests/one-two-three.ls', output)
        self.assertEqual('1\n2\n3\n4\n5\n6\n', output.getvalue())
