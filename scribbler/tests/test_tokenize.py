#!/usr/bin/env python3
"""Tests for the tokenising tools."""

import tempfile
from unittest import TestCase

from tokenization import (
    DefineToken,
    file_token_stream,
    FirstToken,
    text_token_stream,
    make_token,
    IntegerToken,
    PeriodToken,
    Token,
    WordToken,
    )


class TestMakeToken(TestCase):

    def test_make_token_period(self):
        (token, string) = make_token('.')
        self.assertIsInstance(token, PeriodToken)
        self.assertEqual('.', token.text)
        self.assertEqual('', string)

    def test_make_token_whitespace(self):
        (token, string) = make_token('  	')
        self.assertIsNone(token)
        self.assertEqual('', string)

    def test_make_token_first_word(self):
        (token, string) = make_token('Hello')
        self.assertIsInstance(token, FirstToken)
        self.assertEqual('Hello', token.text)
        self.assertEqual('', string)

    def test_make_token_word(self):
        (token, string) = make_token('world ')
        self.assertIsInstance(token, WordToken)
        self.assertEqual('world', token.text)
        self.assertEqual(' ', string)

    def test_make_token_two_words(self):
        (token, string) = make_token('  Hello world ')
        self.assertIsInstance(token, FirstToken)
        self.assertEqual('Hello', token.text)
        self.assertEqual(' world ', string)


class TestToken(TestCase):

    def test_token_repr(self):
        self.assertEqual("PeriodToken()", repr(PeriodToken()))
        self.assertEqual("FirstToken('First')", repr(FirstToken('First')))
        self.assertEqual("WordToken('second')", repr(WordToken('second')))
        self.assertEqual("DefineToken()", repr(DefineToken('Define')))
        self.assertEqual("IntegerToken('101')", repr(IntegerToken('101')))

    def test_token_check(self):
        with self.assertRaises(ValueError):
            FirstToken('following')
        with self.assertRaises(ValueError):
            IntegerToken('101\n')


class TestSimpleStreams(TestCase):

    def test_text_token_stream(self):
        tokens = list(text_token_stream('  Hello world. '))
        self.assertEqual([FirstToken('Hello'),
                          WordToken('world'),
                          PeriodToken('.')], tokens)

    def test_file_token_stream(self):
        with tempfile.NamedTemporaryFile() as file:
            file.write(b'''Hello world.
            This is a test.''')
            file.seek(0)
            tokens = list(file_token_stream(file.name))
        self.assertEqual([
            FirstToken('Hello'), WordToken('world'),
            PeriodToken('.'), FirstToken('This'),
            WordToken('is'), WordToken('a'),
            WordToken('test'), PeriodToken('.'),
            ], tokens)
