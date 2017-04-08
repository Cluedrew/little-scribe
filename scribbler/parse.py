#!/usr/bin/env python3
"""The parser for Little Scribe."""

import sys


from scope import (
    Scope,
    )
from tokenization import (
    FirstToken,
    PeriodToken,
    Token,
    ValueToken,
    WordToken,
    )


class Sentence:
    """A Sentence is a Little Scribe expression.

    Each also repersents a node on the parse graph, and has a list of
    Sentences and Tokens, the children of the node."""

    ChildTypes = '(Sentence, Token)'

    def __init__(self, init=None):
        """Create a new Sentence structure.

        :param init: Either None, a Token, or an interable of ChildTypes."""
        self._children = []
        if isinstance(init, Token):
            self._children.append(init)
        elif init is None:
            pass
        elif hasattr(init, '__iter__'):
            for child in init:
                if not isinstance(child, Sentence.ChildTypes):
                    raise TypeError('Sentence provided with non-child type')
                self._children.append(child)

    def __getitem__(self, index):
        return self._children[index]

    def __len__(self):
        return len(self._children)

    def __iter__(self):
        return iter(self._children)

    def append(self, child):
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

    def ends_with_dot(self):
        if isinstance(self._children[-1], PeriodToken):
            return True
        if isinstance(self._children[-1], Sentence):
            return self._children[-1].ends_with_dot()
        return False

Sentence.ChildTypes = (Sentence, Token)


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


class Parser:
    """This class repersents a parser."""

    def __init__(self, token_stream):
        self.token_stream = token_stream
        self.head = None
        self._token_iterator = Parser._Iter(self)

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
        token = self._next_token()
        if isinstance(token, ValueToken):
            return Sentence([token])
        elif not isinstance(token, FirstToken):
            raise ParseError(
                'Cannot begin a sentence with "' + str(token) + '"')
        node = Sentence([token])
        part_match = scope.new_matcher()
        for token in self._token_iterator:
            if isinstance(token, FirstToken):
                self._push_back(token)
                sub = part_match.sub_type()
                if sub is SUBSENTENCE:
                    node.append(self.parse_expression(scope))
                    part_match.next_sub()
                elif sub is SUBSIGNATURE:
                    node.append(self.parse_signature(scope))
                    part_match.next_sub()
                else:
                    raise ParseError('Sentence not matched.')
            elif isinstance(token, WordToken):
                if part_match.next(token):
                    node.append(token)
                # TODO It might be simpler if we follow the iterator instead.
                elif (isinstance(node[-1], Sentence) and
                      node[-1].ends_with_dot() and
                      part_match.has_end()):
                    return node
                else:
                    raise ParseError('Sentence not matched.')
            elif isinstance(token, PeriodToken):
                if part_match.end():
                    return node
                else:
                    raise ParseError('Sentence not matched.')
            elif isinstance(token, ValueToken):
                node.append(Sentence([token]))
            else:
                raise ValueError('Unknown Token Kind: {}'.format(type(token)))

    def parse_signature(self):
        """Take a stream of tokens and create a Signature.

        Signatures have stricter rules than other parts of the language, but
        they are context insensitive and don't have to match definitions.
        This will use tokens from the stream, but may not empty the stream.

        :return: A Sentence reperesenting the sentence."""
        token = self._next_token()
        if not isinstance(token, FirstToken):
            raise ParseError('Invalid start of Signature: ' + str(token))
        node = Sentence([token])
        for token in self._token_iterator:
            if isinstance(token, FirstToken):
                self._push_back(token)
                node.append(self.parse_signature())
            elif isinstance(token, WordToken):
                node.append(token)
            elif isinstance(token, PeriodToken):
                node.append(token)
                return node
            # TODO Should this be legal?
            elif isinstance(token, ValueToken):
                node.append(Sentence([token]))
            else:
                raise ValueError('Unknown Token Kind: {}'.format(type(token)))

    class _Iter:
        """A convenience iterator for internal use in Parser."""

        def __init__(self, parser):
            self.parser = parser

        def __iter__(self):
            return self

        def __next__(self):
            return self.parser._next_token()
