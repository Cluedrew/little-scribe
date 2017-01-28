#!/usr/bin/env python3
"""Tokenising modual for Little Scribe.

Here tokenisation is responsible for converting a text stream into a stream
of tokens. It provides the Token class and various token stream classes."""


import re
import string


from tree import ParseTreeNode
from signature import SignatureElement


class Token(ParseTreeNode, SignatureElement):
    """Repersents a 'word' of the language.

    Tokens are leaf nodes in the parse tree."""

    def __init__(self, text):
        if not self.regex_match(text):
            raise ValueError('Text does not match regex in Token.')
        self.text = text

    def write(self, to=sys.stdout, prefix=''):
        print(prefix, self.text, file=to)

    @classmethod
    def regex_match(cls, text):
        """Check to see if this text matches the class's regex."""
        return cls.regex.fullmatch(text)

    def __eq__(self, other):
        if not isinstance(other, Token):
            raise TypeError('Tokens can only be equal to other Tokens.')
        return (self.kind == other.kind) and (self.text == other.text)

    def __str__(self):
        return self.text

    def __repr__(self):
        raise NotImplementedError()


class PeriodToken(Token):
    """The Token that appears at the end of a Sentence."""

    regex = re.compile('\.')

    def __init__(self, text='.'):
        super(PeriodToken, self).__init__(text)

    def __repr__(self):
        return 'PeriodToken()'


class FirstToken(Token):
    """A Token that appears at the begining of a Sentence."""

    regex = re.compile(
        '[{0.ascii_uppercase}][{0.ascii_lowercase}]*'.format(string))

    def __init__(self, text):
        super(FirstToken, self).__init__(text)

    def __repr__(self):
        return 'FirstToken({!r})'.format(self.text)


class WordToken(Token):
    """A Token that makes up the middle of a Sentence."""

    regex = re.compile('[{0.ascii_lowercase}]+'.format(string))

    def __init__(self, text):
        super(WordToken, self).__init__(text)

    def __repr__(self):
        return 'WordToken({!r})'.format(self.text)


class NumberToken(Token):
    """A value Token repersenting an Integer value."""

    def __init__(self, text):
        super(NumberToken, self).__init__(text)

    def __repr__(self):
        return 'NumberToken({!r})'.format(self.text)


WHITESPACE_EXP = re.compile('[{0.whitespace}]+'.format(string))
WORD_EXP = re.compile('[{0.ascii_lowercase}]+'.format(string))
FIRST_WORD_EXP = re.compile(
    '[{0.ascii_uppercase}][{0.ascii_lowercase}]*'.format(string))
PERIOD_EXP = re.compile('\.')
NUMBER_EXP = re.compile('[{0.digits}]+'.format(string))

token_regexes = {
    'first-word': FIRST_WORD_EXP,
    'word': WORD_EXP,
    'period': PERIOD_EXP,
    'number': NUMBER_EXP,
    }

# A set of Token child types.
token_types = {WordToken, FirstToken, PeriodToken, NumberToken}


def make_token(source_string):
    """Pull off the first token in the source string.

    :return: A tuple with a Token in the first slot (or None if no Token
        could be generated) and the remaining section of source string.
        This may be different even if no token was made, leading whitespace
        will be removed."""
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


def line_token_stream(line_text):
    """Convert a single line into a stream of tokens."""
    while line_text:
        (token, line_text) = make_token(line_text)
        if token:
            yield token


def file_token_stream(file_name):
    """Convert a text file into a stream of tokens."""
    with open(file_name) as file:
        for line in file.readlines():
            for token in line_token_stream(line):
                yield token
