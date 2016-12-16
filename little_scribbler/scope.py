#!/usr/bin/env python3


class Scope:
    """Repersents a collection of definitions in Little Scribe."""

    def __init__(self, parent=None):
        self.parent = parent


class Definition:
    """Repersents a function definition in Little Scribe."""

    def __init__(self, signature, body):
        self.sig = signature
        self.body = body

    def __call__(self, args):
        """Evaluate the function for a given set of arguments."""
        return self.body(args)

    def __getitem__(self, index)
        if isinstance(index, int):
            return self.sig[index]
        else:
            raise IndexError()


class DefinitionMatchGroup:
    """A group of definitions that match a given prefix."""

    def __init__(self, matching, prefix):
        self.matching = matching
        self.prefix = prefix

    def next_match(self, word):
        at = len(self.prefix)
        new_matching = []
        for index, match in self.matching:
            if match[at] == word:
                new_matching.append(self.matching[index])
        return DefinitionMatchGroup(new_matching, self.prefix + [word])
