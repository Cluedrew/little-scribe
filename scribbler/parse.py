#!/usr/bin/env python3
"""The parser for Little Scribe."""

import sys


from scope import (
    Scope,
    )
from tree import (
    Paragraph,
    Sentence,
    Token,
    )


class UnfinishedSentencesError(Exception):

    def __init__(self, count):
        self.count = count

    def inc(self):
        self.count += 1

    def __repr__(self):
        return 'UnfinshedSentencesError({})'.format(self.count)


class ParseError(Exception):
    """Base Exception for the parse modual."""


class SentenceMisMatchError(ParseError):
    """A Sentence does not match any in the scope."""


class SentenceUnfinisedError(ParseError):
    """A Sentence was not finished."""


class ParseIter:
    """A convenience iterator for internal use in the Parser."""

    def __init__(self, parser):
        self.parser = parser

    def __iter__(self):
        return self

    def __next__(self):
        return self.parser._next_token()


class Parser:
    """This class repersents a parser."""

    def __init__(self, token_stream):
        self.token_stream = token_stream
        self.head = None
        self._token_iterator = ParseIter(self)

    def _next_token(self):
        """Get the next token, either from the stream or the stored head."""
        if self.head is not None:
            token = self.head
            self.head = None
            return token
        return next(self.token_stream)

    def _push_back(self, token):
        """Return a token to the front of the stream."""
        if self.head is None:
            self.head = token
        else:
            raise ValueError('There is already a old head.')

    def _stream_not_empty(self):
        """Are there tokens left to parse?"""
        if self.head is not None:
            return True
        try:
            self._push_back(self._next_token())
        except StopIteration:
            return False
        else:
            return True

    def parse_page(self):
        """Parse a page of Little Scribe code."""
        scope = Scope()
        while self._stream_not_empty():
            paragraph = self.parse_paragraph(scope)

    def parse_paragraph(self, scope):
        """Parse a paragraph.

        :param scope: The scope the paragraph is being parsed within.
        :return: A Paragraph"""
        #return Paragraph(self.parse_expression(scope).children)
        return Paragraph(self.parse_signature().children)

    def parse_sentence(self, scope):
        pass

    # WIP: Useful feature but not needed to get it working.
    def parse_expression(self, scope):
        """Parse an expression.

        Expressions may contain other forms as well, a expression is the
        'other' type of sentence. They must match a known of sentence in
        the scope.

        :param scope: The scope the expression is being parsed within.
        :return: A Sentence."""
        children = []
        for token in self._token_iterator:
            if token.kind == 'first-word':
                self._push_back(token)
                # I need a way to check if it should be a expression or a
                # signature. Is it part of the definition?
                children.append(self.parse_expression(scope))
                if not scope.match_prefix(children):
                    raise ParseError('Sentence not matched.')
            elif token.kind == 'word':
                children.append(token)
                if not scope.match_prefix(children):
                    if (children[-1].ends_with_dot() and
                            scope.match_to_end(children)):
                        return Sentence(children)
                    raise ParseError('Sentence not matched.')
            elif token.kind == 'period':
                children.append(token)
                if scope.match_exact(children):
                    return Sentence(children)
                else:
                    raise ParseError('Sentence not matched.')
            else:
                raise ValueError('Unknown Token.kind: {}'.format(token.kind))

    def parse_signature(self):
        """Take a stream of tokens and create a Signature.

        Signatures have stricter rules than other parts of the language, but
        they are context insensitive and don't have to match definitions.
        This will use tokens from the stream, but may not empty the stream.

        :return: A Sentence reperesenting the sentence."""
        children = []
        for token in self._token_iterator:
            if token.kind == 'first-word' and children:
                self._push_back(token)
                children.append(self.parse_signature())
            elif token.kind in ('first-word', 'word'):
                children.append(token)
            elif token.kind == 'period':
                children.append(token)
                return Sentence(children)
            else:
                raise ValueError('Unknown Token.kind: {}'.format(token.kind))
