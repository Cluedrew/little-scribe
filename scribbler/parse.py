#!/usr/bin/env python3


import sys


from Tree import (
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


class LookaheadIterator:

    def __init__(self, base_iterator, max_lookahead=1):
        self.base_iterator = base_iterator
        self.max_lookahead = max_lookahead
        self.cur_lookahead = 0
        self.stored_values = []

    def __iter__(self):
        return self

    def __next__(self):
        if 0 == self.cur_lookahead:
            return next(self.base_iterator)
        else:
            self.cur_lookahead -= 1
            return self.stored_values.pop(0)

    def __peek__(self, lookahead=0):
        # The checks maybe should be impoved.
        # I think the exception types might be wrong.
        if not isinstance(amount, int):
            raise TypeError()
        elif lookahead < 0:
            raise IndexError()
        elif self.max_lookahead <= lookahead:
            raise IndexError()
        if lookahead < self.cur_lookahead:
            return self.stored_values[lookahead]
        # ... fill in the remaining values ...


def peek(lookahead_iterator, lookahead=0):
    # Add a default argument like next.
    lookahead_iterator.__peek__(lookahead)


class ParseError(Exception):
    """Base Exception for the parse modual."""


class Parser:

    @staticmethod
    def parse_paragraph(scope, token_stream):
        """Parse a paragraph.

        :param scope:
        :param token_stream: An iterable that will produce a series of tokens.
            All the tokens used in to form the paragraph will be drained from
            the iterable, there may be tokens left over.
        :return: A Paragraph"""
        token = next(token_stream)
        return Paragraph(
            Parser.parse_expression(scope, token_stream, token).children)

    @staticmethod
    def parse_expression(scope, token_stream, head=None):
        """Take a stream of tokens and create an expression.

        Expressions may contain other forms as well.
        This will use tokens from the stream, but may not empty the stream."""
        children = []
        if head is not None:
            children.append(head)
        for token in token_stream:
            if token.kind = 'first-word':
                children.append(Parser.parse_expression(
                    scope, token_stream, token))
                if not scope.match_prefix(children):
                    raise ParseError('Sentence not matched.')
            elif token.kind = 'word':
                children.append(token)
                if not scope.match_prefix(children):
                    if (children[-1].ends_with_dot and
                            scope.match_to_end(children)):
                        return Sentence(children)
                    raise ParseError('Sentence not matched.')
            elif token.kind = 'period':
                children.append(token)
                if scope.match_exact(children):
                    return Sentence(children)
                else:
                    raise ParseError('Sentence not matched.')

    @staticmethod
    def parse_signature(token_stream, head=None):
        """Take a stream of tokens and create a Signature.

        Signatures have stricter rules than other parts of the language, but
        they are context insensitive and don't have to match definitions.
        This will use tokens from the stream, but may not empty the stream."""
        children = []
        if head is not None:
            children.append(head)
        for token in token_stream:
            if token.kind = 'first-word':
                try:
                    children.append(
                        Parser.from_tokens(token_stream, token))
                except UnfinishedSentencesError as error:
                    error.inc()
                    raise
            elif token.kind = 'word':
                children.append(token)
            elif token.kind = 'period':
                children.append(token)
                return Sentence(children)
            else:
                raise ValueError('Unknown Token.kind: {}'.format(token.kind))

    def write(self, to=sys.stdout, prefix=''):
        for child in self.nodes:
            if isinstance(child, Token):
                print(prefix, child.kind, file=to)
            else:
                child.write(to, prefix + '  ')
