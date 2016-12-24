#!/usr/bin/env python3
"""Tests for the tokenising tools."""

import tempfile
from unittest import TestCase

from tree import Token
from tokenise import (
    file_token_stream,
    line_token_stream,
    make_token,
    )


class TestMakeToken(TestCase):

    def test_make_token_period(self):
        (token, string) = make_token('.')
        self.assertEqual('period', token.kind)
        self.assertEqual('.', token.text)
        self.assertEqual('', string)

    def test_make_token_whitespace(self):
        (token, string) = make_token('  	')
        self.assertIsNone(token)
        self.assertEqual('', string)

    def test_make_token_first_word(self):
        (token, string) = make_token('Hello')
        self.assertEqual('first-word', token.kind)
        self.assertEqual('Hello', token.text)
        self.assertEqual('', string)

    def test_make_token_word(self):
        (token, string) = make_token('world ')
        self.assertEqual('word', token.kind)
        self.assertEqual('world', token.text)
        self.assertEqual(' ', string)

    def test_make_token_two_words(self):
        (token, string) = make_token('  Hello world ')
        self.assertEqual('first-word', token.kind)
        self.assertEqual('Hello', token.text)
        self.assertEqual(' world ', string)


class TestSimpleStreams(TestCase):

    def test_line_token_stream(self):
        tokens = list(line_token_stream('  Hello world. '))
        self.assertEqual([Token('first-word', 'Hello'),
                          Token('word', 'world'),
                          Token('period', '.')], tokens)

    def test_file_token_stream(self):
        with tempfile.NamedTemporaryFile() as file:
            file.write(b'''Hello world.
            This is a test.''')
            file.seek(0)
            tokens = list(file_token_stream(file.name))
        self.assertEqual([
            Token('first-word', 'Hello'), Token('word', 'world'),
            Token('period', '.'), Token('first-word', 'This'),
            Token('word', 'is'), Token('word', 'a'),
            Token('word', 'test'), Token('period', '.'),
            ], tokens)
