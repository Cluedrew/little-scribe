#!/usr/bin/env python3
"""Tokeniser modual for Little Scribe.

Here tokenisation is responsible for converting a text stream into a stream
of tokens. It provides the Token class and various token stream classes."""


import re
import string


class Token:
    """Repersents a 'word' of input."""

    def __init__(self, kind, text):
        self.kind = kind
        self.text = text


class Tokeniser:
    """A low level tokenising tool."""

    WHITESPACE_EXP = re.compile('[{0.whitespace}]+'.format(string))
    WORD_EXP = re.compile('[{0.ascii_lowercase}]+'.format(string))
    FIRST_WORD_EXP = re.compile(
        '[{0.ascii_uppercase}][{0.ascii_lowercase}]*'.format(string))
    PERIOD_EXP = re.compile('\.')

    token_regexes = {
        'first-word': FIRST_WORD_EXP,
        'word': WORD_EXP,
        'period': PERIOD_EXP,
        }

    @staticmethod
    def make_token(source_string):
        """Pull off the first token in the source string.

        :return: (Token, str) """
        whitespace_match = WHITESPACE_EXP.match(source_string)
        if whitespace_match:
            source_string = source_string[whitespace_match.end():]
        for token_kind, token_exp in token_regexes.items():
            token_match = token_exp.match(source_string)
            if token_match:
                return (Token(token_kind, token_match.group()),
                        source_string[token_match.end():])
        else:
            return (None, source_string)


class TokenStream:
    """The basic TokenStream."""

    def __init__(self):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        pass


def line_token_stream(line_text):
    """Convert a single line into a stream of tokens."""
    while line_text:
        (token, line_text) = Tokeniser.make_token(line_text)
        if token:
            yield token


def file_token_stream(file_name):
    """Convert a text file into a stream of tokens."""
    with open(file_name) as file:
        for line in file.readlines():
            for token in line_token_stream(line):
                yield token
