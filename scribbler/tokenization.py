#!/usr/bin/env python3
"""Tokenising modual for Little Scribe.

Here tokenization is responsible for converting a text stream into a stream
of tokens. It provides the Token class and various token stream classes."""


import re
import string
import sys


class Token:
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
        return (self.text == other.text) and (type(self) == type(other))

    def __ne__(self, other):
        return not self == other

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


class DefineToken(FirstToken):

    regex = re.compile('Define')

    def __init__(self, text='Define'):
        super(DefineToken, self).__init__(text)

    def __repr__(self):
        return 'DefineToken()'


class WordToken(Token):
    """A Token that makes up the middle of a Sentence."""

    regex = re.compile('[{0.ascii_lowercase}]+'.format(string))

    def __init__(self, text):
        super(WordToken, self).__init__(text)

    def __repr__(self):
        return 'WordToken({!r})'.format(self.text)


class ValueToken(Token):
    """A value Token is a hard coded value, is an entire sentence."""

    def get_value(self):
        raise NotImplementedError()


class NumberToken(ValueToken):
    """A value Token repersenting an Integer value."""

    regex = re.compile('[{0.digits}]+'.format(string))

    def __init__(self, text):
        super(NumberToken, self).__init__(text)

    def __repr__(self):
        return 'NumberToken({!r})'.format(self.text)

    def get_value(self):
        return int(self.text)


WHITESPACE_EXP = re.compile('[{0.whitespace}]+'.format(string))

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
    for token_kind in token_types:
        token_match = token_kind.regex.match(source_string)
        if token_match:
            return (token_kind(token_match.group()),
                    source_string[token_match.end():])
    else:
        return (None, source_string)


def text_token_stream(base_text):
    """Convert a single line into a stream of tokens."""
    while base_text:
        (token, base_text) = make_token(base_text)
        if token:
            yield token


def file_token_stream(file_name):
    """Convert a text file into a stream of tokens."""
    with open(file_name) as file:
        for line in file.readlines():
            for token in text_token_stream(line):
                yield token


def tokenify(text):
    """Convert a string to token, must convert exactly."""
    for token_kind in token_types:
        token_match = token_kind.regex.fullmatch(text)
        if token_match:
            return token_kind(text)
    else:
        raise ValueError('tokenify: \'' + text + '\' is not a token.')


def tokenify_list(text_list):
    """Convert a list of strings into a list of tokens."""
    return [tokenify(text) for text in text_list]
