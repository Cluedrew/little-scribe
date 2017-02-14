#!/usr/bin/env python3
"""The various types that repersent nodes in the parse tree."""

# Clear it out. We only need Sentence and the already exported Token.


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
        """Create a new Sentence structure.

        :param children: A list of children to this node. All should be
            some time of ParseTreeNode."""
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
        super(Paragraph, self).write(to, prefix)


class Pattern(ParseTreeNode):
    """A Pattern that other sentences can match against."""

    def __init__(self, children):
        self.children = children

    def get_signature(self):
        """Create the signature that this Pattern defines."""
        # Circular dependancy.
