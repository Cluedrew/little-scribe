#!/usr/bin/env python3

import sys


class ParseTreeNode:
    """Repersents a node in the parse tree."""

    def write(self, to=sys.stdout, prefix=''):
        print(prefix + '<unknown>', file=to)


class Sentence(ParseTreeNode):
    """A branch in the tree node."""

    def __init__(self, children):
        self.children = children

    def write(self, to=sys.stdout, prefix=''):
        for child in self.children:
            if isinstance(child, Token):
                child.write(to, prefix)
            else:
                child.write(to, prefix + '  ')

    def ends_with_dot(self):
        last = self.children[-1]
        if isinstance(last, Token) and last.kind == 'period':
            return True
        elif isinstance(last, Sentence) and last.ends_with_dot():
            return True
        else:
            return False


class Paragraph(Sentence):
    """A top level sentence that is not part of another sentence."""

    def write(self, to=sys.stdout, prefix=''):
        if '' != prefix:
            raise ValueError('Paragraph not at top level.')
        super().write(to, prefix)


class Token(ParseTreeNode):
    """Repersents a 'word' of the language.

    Tokens are leaf nodes in the parse tree."""

    def __init__(self, kind, text):
        self.kind = kind
        self.text = text

    def write(self, to=sys.stdout, prefix=''):
        print(prefix, self.text, file=to)

    def __eq__(self, other):
        if not isinstance(other, Token):
            raise TypeError('Tokens can only be equal to other Tokens.')
        return (self.kind == other.kind) and (self.text == other.text)

    def __repr__(self):
        return 'Token({!r}, {!r})'.format(self.kind, self.text)

#   @staticmethod
#   def [new_]period():
#       return Token('period', '.')


class Period(Token):

    def __init__(self):
        super().__init__('period', '.')


class FirstToken(Token):

    def __init__(self, text):
        super().__init__('first-word', text)


class WordToken(Token):

    def __init__(self, text):
        super().__init__('word', text)

