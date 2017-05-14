#!/usr/bin/env python3
"""The parser for Little Scribe."""

import sys


from scope import (
    Definition,
    Scope,
    )
from sentence import (
    Sentence,
    )
from tokenization import (
    FirstToken,
    PeriodToken,
    text_token_stream,
    Token,
    ValueToken,
    WordToken,
    )


class ParseError(Exception):
    """Base Exception for the parse modual."""


class SentenceMisMatchError(ParseError):
    """A Sentence does not match any in the scope."""


class SentenceUnfinisedError(ParseError):
    """A Sentence was not finished."""


class Parser:
    """This class repersents a parser."""

    def __init__(self, token_stream):
        self._token_stream = TokenStream(token_stream)

    def parse_page(self):
        """Parse a page of Little Scribe code."""
        scope = Scope()
        while self._token_stream.not_empty():
            paragraph = self.parse_paragraph(scope)

    def iter_paragraph(self, scope):
        while self._token_stream.not_empty():
            yield self.parse_paragraph(scope)

    def parse_paragraph(self, scope):
        """Parse a paragraph. It is just a wrapper for now.

        :param scope: The scope the paragraph is being parsed within.
        :return: A Sentence"""
        return self.parse_expression(scope)

    def parse_sentence(self, scope):
        return self.parse_expression(scope)

    def parse_expression(self, scope):
        """Parse an expression.

        Expressions may contain other forms as well, a expression is the
        'other' type of sentence. They must match a known of sentence in
        the scope.

        :param scope: The scope the expression is being parsed within.
        :return: A Sentence."""
        token = next(self._token_stream)
        if isinstance(token, str):
            raise Exception('String instead of Token')
        if isinstance(token, ValueToken):
            return Sentence([token])
        elif not isinstance(token, FirstToken):
            raise ParseError(
                'Cannot begin a sentence with \"' + repr(token) + '\"')
        elif 'Define' == token.text:
            self._token_stream.push_back(token)
            return self.parse_definition(scope)
        node = Sentence([token])
        part_match = scope.new_matcher()
        if not part_match.next(token):
            self._token_stream.push_back(token)
            raise ParseError('Sentence not matched.', node)
        for token in self._token_stream:
            if isinstance(token, FirstToken):
                self._token_stream.push_back(token)
                if part_match.next():
                    node.append(self.parse_expression(scope))
                else:
                    raise ParseError('Sentence not matched.', node)
            elif isinstance(token, WordToken):
                if part_match.next(token):
                    node.append(token)
                elif node.ends_with_dot() and part_match.has_end():
                    self._token_stream.push_back(token)
                    return node
                else:
                    raise ParseError('Sentence not matched.', node)
            elif isinstance(token, PeriodToken):
                if part_match.has_end():
                    node.append(token)
                    return node
                else:
                    raise ParseError('Sentence not matched.', node)
            elif isinstance(token, ValueToken):
                node.append(Sentence([token]))
            else:
                raise ValueError('Unknown Token Kind: {}'.format(type(token)))
        if isinstance(node[-1], Sentence) and part_match.has_end():
            return node
        raise ParseError('Sentence not matched.', node)

    def parse_signature(self):
        """Take a stream of tokens and create a Signature.

        Signatures have stricter rules than other parts of the language, but
        they are context insensitive and don't have to match definitions.
        This will use tokens from the stream, but may not empty the stream.

        :return: A Sentence reperesenting the sentence."""
        token = next(self._token_stream)
        if not isinstance(token, FirstToken):
            raise ParseError('Invalid start of Signature: ' + str(token))
        node = Sentence([token])
        for token in self._token_stream:
            if isinstance(token, FirstToken):
                self._token_stream.push_back(token)
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
        raise Exception('Parser.parse_signature: fell out of the loop.')

    @staticmethod
    def make_inner_scope(outer_scope, signature):
        inner_scope = Scope(outer_scope)
        def add_def(base_sentence):
            definition = Definition(base_sentence, None)
            inner_scope.add_definition(definition)
        add_def(signature)
        for sub in signature.iter_sub():
            add_def(el)
        return inner_scope

    def parse_definition(self, outer_scope):
        """Parse a definition from the incomming tokens.

        This is technically a kind of expression, but there are a few special
        rules that may force it to become seperate. This is temporary as it
        is just the fastest way I can get this to work. I hope.

        'Define Function or variable name. to be Body. .'"""
        token = next(self._token_stream)
        if 'Define' != token.text:
            raise ParseError('Invalid start of Definition: ' + str(token))
        node = Sentence(token)
        ptr = outer_scope.new_matcher()
        if not ptr.next(token):
            self._token_stream.push_back(item)
            raise ParseError('Sentence not matched.', node)
        inner_scope = None
        for item in self._token_stream:
            if isinstance(item, FirstToken):
                self._token_stream.push_back(item)
                if ptr.next():
                    if inner_scope is None:
                        signature = self.parse_signature()
                        node.append(signature)
                        inner_scope = self.make_inner_scope(
                            outer_scope, signature)
                    else:
                        node.append(self.parse_expression(inner_scope))
                elif node.ends_with_dot() and ptr.has_end():
                    self._token_stream.push_back(item)
                    return node
                else:
                    raise ParseError('Sentence not matched.', node)
            elif isinstance(item, WordToken):
                if ptr.next(item):
                    node.append(item)
                elif node.ends_with_dot() and ptr.has_end():
                    self._token_stream.push_back(item)
                    return node
                else:
                    raise ParseError('Sentence not matched.', node)
            elif isinstance(item, PeriodToken):
                if ptr.has_end():
                    node.append(item)
                    return node
                else:
                    raise ParseError('Sentence not matched.', node)
            elif isinstance(item, ValueToken):
                if ptr.next():
                    node.append(Sentence(item))
                else:
                    raise ParseError('Sentence not matched.', node)
            else:
                raise TypeError('Parser.parse_definition: Unexpected type' +
                                str(type(item)))
        if node.ends_with_dot() and ptr.has_end():
            return node
        raise ParseError('Sentence not matched.', node)


class TokenStream:

    def __init__(self, iter):
        """Create the TokenStream by wrapping around an iterator.

        :param iter: An iterator that returns Tokens."""
        self.iter = iter
        self.head = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.head is None:
            return next(self.iter)
        next_token = self.head
        self.head = None
        return next_token

    def is_empty(self):
        if self.head is not None:
            return False
        self.head = next(self.iter, None)
        return self.head is None

    def not_empty(self):
        return not self.is_empty()

    def push_back(self, token):
        if self.head is not None:
            raise ValueError('TokenStream.push_back: Already has head.')
        self.head = token


def string_to_signature(text):
    """Convert a string into a signature."""
    parser = Parser(text_token_stream(text))
    return parser.parse_signature()
