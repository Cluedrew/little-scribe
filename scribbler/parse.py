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
        # Interal data array.
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
        # Cache of definition look up.
        self._definition = None

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

    def is_primitive(self):
        return (1 == len(self._children) and
            isinstance(self._children, ValueToken))

    def get_value(self):
        if not self.is_primitive():
            raise ValueError(
                'Sentence.get_value: requires primitive Sentence.')
        return self._children[0].get_value()

    def set_definition(self, definition):
        if self.is_primitive():
            raise ValueError(
                'Sentence.set_definition: requires non-primitive Sentence.')
        self._definition = definition

    def get_definition(self):
        if self.is_primitive():
            raise ValueError(
                'Sentence.get_definition: requires non-primitive Sentence.')
        return self._definition

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
        self._token_stream = TokenStream(token_stream)

    def parse_page(self):
        """Parse a page of Little Scribe code."""
        scope = Scope()
        while self._token_stream.not_empty():
            paragraph = self.parse_paragraph(scope)

    def iter_paragraph(self, scope):
        class _IterParagraph:

            def __init__(self, parser, scope):
                self.parser = parser
                self.scope = scope

            def __iter__(self):
                return self

            def __next__(self):
                return self.parser.parse_paragraph(scope)

        return _IterParagraph(self, scope)

    def parse_paragraph(self, scope):
        """Parse a paragraph. It is just a wrapper for now.

        :param scope: The scope the paragraph is being parsed within.
        :return: A Sentence"""
        return self.parse_expression(scope)

    def parse_sentence(self, scope):
        # Try: do the split expression/signature here, and also handle the
        # start of the sentence.
        start = next(self._token_stream)
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
        token = next(self._token_stream)
        if isinstance(token, ValueToken):
            return Sentence([token])
        elif not isinstance(token, FirstToken):
            raise ParseError(
                'Cannot begin a sentence with "' + str(token) + '"')
        node = Sentence([token])
        part_match = scope.new_matcher()
        for token in self._token_stream:
            if isinstance(token, FirstToken):
                self._token_stream.push_back(token)
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

    def make_inner_scope(self, outer_scope, signature):
        inner_scope = Scope(outer_scope)
        def add_def(base_sentence):
             definition = Definition.from_sentence(base_sentence, None)
             inner_scope.add_definition(definition)
        add_def(signature)
        for el in signature:
            if isinstance(el, Sentence):
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
        sig = self.parse_signature(outer_scope)
        node.append(sig)
        for word in ['to', 'be']:
            token = next(self._token_stream)
            if token.text != word:
                raise ParseError('Did not find ' + word + ' in definition.')
            node.append(token)
        inner_scope = self.make_inner_scope(outer_scope, signature)
        node.append(self.parse_expression(inner_scope))
        if self._token_stream.not_empty():
            token = next(self._token_stream)
            if isinstance(token, PeriodToken):
                node.append(token)
            else:
                self._token_stream.push_back(token)
        return node


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
