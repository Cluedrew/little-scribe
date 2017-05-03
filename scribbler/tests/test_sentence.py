#!/usr/bin/env python3


from sentence import (
    Sentence,
    )
from tokenization import (
    FirstToken,
    PeriodToken,
    WordToken,
    )
from unittest import TestCase


class TestSentence(TestCase):

    def test_equal_operator(self):
        left = Sentence([FirstToken('Height'), WordToken('of'),
                         WordToken('box'), PeriodToken()])
        right = Sentence([FirstToken('Height'), WordToken('of'),
                          WordToken('box'), PeriodToken()])
        self.assertTrue(left == right)

    def test_ends_with_dot_period(self):
        has_period = Sentence([FirstToken('Short'),
                               WordToken('sentence'), PeriodToken()])
        self.assertTrue(has_period.ends_with_dot())
        no_period = Sentence([FirstToken('Word')])
        self.assertFalse(no_period.ends_with_dot())
        super_has_period = Sentence([FirstToken('Run'), has_period])
        self.assertTrue(super_has_period.ends_with_dot())
        super_no_period = Sentence([FirstToken('Run'), no_period])
        self.assertFalse(super_no_period.ends_with_dot())
