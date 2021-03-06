#!/usr/bin/env python3


import sys

from tokenization import (
    PeriodToken,
    Token,
    ValueToken,
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
        if isinstance(init, Sentence.ChildTypes):
            self._children.append(init)
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

    def __eq__(self, other):
        if len(self._children) != len(other._children):
            return False
        for (mine, yours) in zip(self._children, other._children):
            if type(mine) != type(yours) or mine != yours:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    # Two different ways to handle the seperators.
    def __str__(self):
        data = ''
        for word in self._children:
            if isinstance(word, Token):
                seg = str(word)
            else:
                # Recurse?
                seg = '(SUB)'
            if '' == data:
                data = seg
            else:
                data = data + ' ' + seg
        return data

    def __repr__(self):
        text = 'Sentence(['
        iterator = iter(self._children)
        item = next(iterator, None)
        while item:
            if isinstance(item, Token):
                text = text + repr(item)
            else:
                # Recurse?
                text = text + 'Sentence()'
            item = next(iterator, None)
            if item is None:
                break
            text = text + ', '
        return text + '])'

    def append(self, child):
        """Add a new Token to the end of the Sentence."""
        if isinstance(child, Sentence.ChildTypes):
            self._children.append(child)
        else:
            raise TypeError('Sentence provided with non-child type')

    def iter_sub(self):
        """Iterate through the subsentences in this sentence."""
        for item in self._children:
            if isinstance(item, Sentence):
                yield item

    def write(self, to=sys.stdout, prefix=''):
        for child in self.children:
            if isinstance(child, Token):
                child.write(to, prefix)
            else:
                child.write(to, prefix + '  ')

    def ends_with_dot(self):
        last = self._children[-1]
        return (isinstance(last, PeriodToken) or
            (isinstance(last, Sentence) and last.ends_with_dot()))

    def is_primitive(self):
        return (1 == len(self._children) and
            isinstance(self._children[0], ValueToken))

    def get_value(self):
        if not self.is_primitive():
            raise ValueError(
                'Sentence.get_value: requires primitive Sentence.')
        return self._children[0].get_value()

    # get_type(self): -> self._children[0].get_type()


Sentence.ChildTypes = (Sentence, Token)
