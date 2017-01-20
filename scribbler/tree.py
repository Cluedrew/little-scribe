#!/usr/bin/env python3
"""The various types that repersent nodes in the parse tree."""

# I think I shouldn't put so much logic here. It just doesn't seem to fit.
# But where should it go?

import sys


class ParseTreeNode:
    """Repersents a node in the parse tree."""

    def write(self, to=sys.stdout, prefix=''):
        """Write the node and its subnodes."""
        print(prefix + '<unknown>', file=to)

    def evaluate(self, scope):
        """Evaluate the node's value using its contents."""
        raise NotImplementedError()


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

    def _get_definition(self, scope):
        """Get the matching definition of this Sentence from the scope."""

    def _evaluate(self, scope):
        """Evaluate the sentence as a function."""

    def evaluate(self, scope):
        return self._evaluate(scope)

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


# Maybe something like this:
class PeriodToken(Token):

    regex = re.compile('\.')

    # This would be on Token:
    @classmethod
    def regex_match(cls, text):
        """Check to see if this text matches the class's regex."""
        return cls.regex.fullmatch(text)

    def __init__(self, text='.'):
        super(PeriodToken, self).__init__(text)

#class FirstToken(Token):
#class WordToken(Token):
#class NumberToken(Token):
