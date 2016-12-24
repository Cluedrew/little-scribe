#!/usr/bin/env python3


class Scope:
    """Repersents a collection of definitions in Little Scribe."""

    def __init__(self, parent=None):
        """Create a new scope.

        :param parent: If this is a top level scope, parent should be None,
            if not than it should be another scope instance, repersenting
            the lowest level scope this one is nested within."""
        if parent is not None and not isinstance(parent, Scope):
            raise TypeError("Scope's parent must be None or another Scope.")
        self._parent = parent
        self._definitions = []

    def add_definition(self, definition):
        """Add a new definition to the scope.

        It must not conflict with any existing definition in the scope."""

    def merge(self, other):
        """Merge this Scope with another."""

    def match_first(self, first_word):
        """Match definitions that start with first_word."""

    def match_prefix(self, prefix):
        """Match definitions that start with prefix."""

    def match_to_end(self, prefix):
        """Match definitions that start with prefix up to the period."""


class SubSentence:
    """Repersents a sub-sentence in a function signature."""

    def __init__(self, value):
        self.value = value


sub_signature = SubSentence(True)
sub_expression = SubSentence(False)


class Definition:
    """Repersents a function definition in Little Scribe."""

    def __init__(self, signature, body):
        """Create the definition from its signature and the code body.

        :param signature: A list that repersents the signature.
        :param body: A callable that repersents the operation the definition
            preforms on its parameters."""
        self.sig = signature
        self.body = body

    def __call__(self, args):
        """Evaluate the function for a given set of arguments."""
        return self.body(args)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.sig[index]
        else:
            raise TypeError()

    def __len__(self):
        return len(self.sig)


class DefinitionMatchGroup:
    """A group of definitions that match a given prefix."""

    def __init__(self, matching, prefix):
        self.matching = matching
        self.prefix = prefix

    def next_match(self, word):
        """Create a new group that matches a subset of this group.

        The Definitions that match prefix + [word] are matched."""
        at = len(self.prefix)
        new_matching = []
        for index, match in self.matching:
            if match[at] == word:
                new_matching.append(self.matching[index])
        return DefinitionMatchGroup(new_matching, self.prefix + [word])

    def __len__(self):
        return len(self.matching)

    def __iter__(self):
        return iter(self.matching)

    def __bool__(self):
        return bool(self.matching)
