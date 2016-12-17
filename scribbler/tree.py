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
