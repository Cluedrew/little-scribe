#!/usr/bin/env python3
"""The parser for Little Scribe."""

import sys


from scope import (
    Scope,
    )
from tokenize import (
    Token,
    )

class Sentence:
    """A Sentence is a Little Scribe expression.

    They are lists of Tokens and Sentences, the children of the node."""

    ChildTypes = (Sentence, Token)

    def __init__(self, iter=None):
        """Create a new Sentence structure.

        :param children: A list of children to this node. All should be
            some time of ParseTreeNode."""
        self._children = []
        for child in iter:
            if isinstance(child, Sentence.ChildTypes):
                self._children.append(child)
            else:
                raise TypeError('Sentence provided with non-child type')

    def __getitem__(self, index):
        return self._children[index]

    def __len__(self):
        return len(self._children)

    def append(self, child)
        """Add a new Token to the end of the Sentence."""
        if isinstance(child, Sentence.ChildTypes):
            self._children.append(child)
        else:
            raise TypeError('Sentence provided with non-child type')

    def write(self, to=sys.stdout, prefix=''):
        for child in self.children:
            if isinstance(child, Token):
                child.write(to, prefix)
            else:
                child.write(to, prefix + '  ')


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


class _ParseIter:
    """A convenience iterator for internal use in Parser."""

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
        self._token_iterator = _ParseIter(self)

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
        # Try: do the split expression/signature here, and also handle the
        # start of the sentence.
        start = self._next_token()
        # Check Start
        node = Sentence([start])
        if some_condition:
            return self.parse_expression(scope, node)
        else:
            return self.parse_signature(scope, node)

    def parse_expression(self, scope):
        """Parse an expression.

        Expressions may contain other forms as well, a expression is the
        'other' type of sentence. They must match a known of sentence in
        the scope.

        :param scope: The scope the expression is being parsed within.
        :return: A Sentence."""
        node = Sentence()
        # Some sort of tracker for the definitions we are matching.
        part_match = scope.new_definition()
        for token in self._token_iterator:
            if isinstance(token, FirstToken):
                self._push_back(token)
                # Split must happen here, expression or signature?
                # Something like:
                sub = part_match.subsentence_type()
                if sub = SubExpression:
                    node.append(self.parse_expression(scope))
                elif sub = SubSignature:
                    node.append(self.parse_signature(scope))
                else:
                    raise ParseError('Sentence not matched.')
            elif isinstance(token, WordToken):
                if part_match.continues_on(token):
                    node.append(token)
                elif node.last().ends_with_dot() and part_match.complete():
                    return node
                else:
                    raise ParseError('Sentence not matched.')
            elif isinstance(token, PeriodToken):
                if part_match.complete():
                    return node
                else:
                    raise ParseError('Sentence not matched.')
            elif isinstance(token, NumberToken):
                node.append(Sentence([token])
            else:
                raise ValueError('Unknown Token Kind: {}'.format(type(token)))

    def parse_signature(self):
        """Take a stream of tokens and create a Signature.

        Signatures have stricter rules than other parts of the language, but
        they are context insensitive and don't have to match definitions.
        This will use tokens from the stream, but may not empty the stream.

        :return: A Sentence reperesenting the sentence."""
        node = Sentence()
        for token in self._token_iterator:
            if isinstance(token, FirstToken) and node:
                self._push_back(token)
                node.append(self.parse_signature())
            elif isinstance(token, (FirstToken, WordToken)):
                node.append(token)
            elif isinstance(token, PeriodToken):
                node.append(token)
                return Sentence(children)
            elif isinstance(token, NumberToken):
                node.append(Sentence([token]))
            else:
                raise ValueError('Unknown Token.kind: {}'.format(token.kind))
