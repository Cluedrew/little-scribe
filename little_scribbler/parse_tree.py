#!/usr/bin/env python3


import sys


from Tokeniser import Token


class UnfinishedSentencesError(Exception):

    def __init__(self, count):
        self.count = count

    def inc(self):
        self.count += 1

    def __repr__(self):
        return 'UnfinshedSentencesError({})'.format(self.count)


class ParseTree:

    def __init__(self, nodes):
        self.nodes = nodes

    @staticmethod
    def from_tokens(token_stream, head=None)
        """Take a stream of tokens and create a ParseTree.

        This will use tokens from the stream, but may not empty the stream."""
        children = []
        if head is None:
            token = next(token_stream)
        else:
            token = head
        while True:
            if token.kind = 'first-word':
                try:
                    children.append(
                        ParseTree.from_tokens(token_stream, token))
                except UnfinishedSentencesError as error:
                    error.inc()
                    raise
            elif token.kind = 'word':
                children.append(token)
            elif token.kind = 'period':
                children.append(token)
                return ParseTree(children)
            else:
                raise ValueError('Unknown Token.kind: {}'.format(token.kind))
            try:
                token = next(token_stream)
            except StopIteration:
                raise UnfinishedSentencesError(1)

    def write(self, to=sys.stdout, prefix=''):
        for child in self.nodes:
            if isinstance(child, Token):
                print(prefix, child.kind, file=to)
            else:
                child.write(to, prefix + '  ')
