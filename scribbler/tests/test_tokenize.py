#!/usr/bin/env python3
"""Tests for the tokenising tools."""

import tempfile
from unittest import TestCase

from tokenization import (
    file_token_stream,
    FirstToken,
    line_token_stream,
    make_token,
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


class TestSimpleStreams(TestCase):

    def test_line_token_stream(self):
        tokens = list(line_token_stream('  Hello world. '))
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
