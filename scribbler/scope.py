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
        self._root = Scope._Node()

    def _iter_definitions(self):
        for definition in self._definitions:
            yield definition
        if self._parent is not None:
            for definition in self._parent._iter_definitions():
                yield definition

    def _add_to_tree(self, definition):
        node = self._root
        for el in definition.pattern:
            if isinstance(el, Token):
                for t,n in node.tokens:
                    if t == el:
                        node = n
                        break
                else:
                    # Error
            elif el is SUBSENTENCE:
                if node.subsentence is SUBSENTENCE:
                    node = node.subs_node
                else:
                    # Error
            elif el is SUBSIGNATURE:
                if node.subsentence is SUBSIGNATURE:
                    node = node.subs_node
                else:
                    # Error
            else:
                # Error


    def add_definition(self, definition):
        """Add a new definition to the scope.

        It must not conflict with any existing definition in the scope."""
        for existing in self._iter_definitions():
            if existing.has_conflict(definition):
                raise ValueError('New definition conflicts with existing '
                                 'definition in scope.')
        else:
            self._definitions.append(definition)
            self._add_to_tree(definition)

    def merge(self, other):
        """Merge another Scope into this one."""
        # Weak exception garenty.
        for definition in other._iter_definitions():
            for existing in self._iter_definitions():
                if existing is definition:
                    break
                if existing.has_conflicts(definition):
                    raise ValueError('Conflicting definitions in merging '
                                     'scopes.')
            else:
                # This is adding to the same list its reading from.
                self._definitions.append(definition)

    def match_first(self, first_word):
        """Match definitions that start with first_word."""
        group = DefinitionMatchGroup([first_word])
        for definition in self._definitions:
            if first_word == definition[0]:
                group.matching.append(definition)
        return group

    def match_prefix(self, prefix):
        """Match definitions that start with prefix."""
        group = DefinitionMatchGroup(prefix)
        for definition in self._definitions:
            for i in range(len(prefix)):
                if prefix[i] != definition[i]:
                    break
            else:
                group.matching.append(definition)
        return group

    def match_to_end(self, sentence):
        """Match definitions that start with prefix up to the period.

        [The period might become optional at some point.]"""
        has_period = (isinstance(sentence[-1], Token) and
                      sentence[-1].kind == 'period')
        # Go through every definition.
        for definition in self._definitions:
            # Search for a mismatch.
            for (i, word) in enumerate(definition):
                if word is sub_expression:
                    if not isinstance(sentence[i], Sentence):
                        break
                elif isinstance(word, Token):
                    if (word.kind != sentence[i].kind or
                            word.text != sentence[i].text):
                        break
            else:
                return DefinitionMatchGroup(sentence, definition)
        else:
            return DefinitionMatchGroup(sentence)

    class _Node:
        """Internal class used in constructing a tri, to store definions."""

        def __init__(self)
            self.subsentence = None
            self.subs_node = None
            self.tokens = []
            self.definition = None


DEF_DIFF_MATCH = 'match'
DEF_DIFF_CONFLICT = 'conflict'
DEF_DIFF_UNIQUE = 'unique'

class Definition:
    """A Definition in Little Scribe. Currently only function definitions."""

    @staticmethod
    def from_define(head, body):
        """Create a new function Definition from the Define.

        :param head: The Sentence that defines the function signature.
        :param body: The Sentence that defines the function body."""
        pass

    @staticmethod
    def _diff_element(self_el, other_el):
        """Difference level between two elements of a definition signature."""
        are_tokens = [
            isinstance(self_el, Token), isinstance(other_el, Token)]
        if all(are_tokens):
            return DEF_DIFF_MATCH if self_el == other_el else DEF_DIFF_UNIQUE
        if any(are_tokens):
            return DEF_DIFF_UNIQUE
        return DEF_DIFF_MATCH if self_el == other_el else DEF_DIFF_CONFLICT

    def diff(self, other):
        """Get the level of difference between two definitions."""
        if not isinstance(other, Signature):
            raise TypeError('diff: other is not a Signature')
        for (self_element, other_element) in zip(self._tokens, other._tokens):
            result = self._diff_element(self_element, other_element)
            if DEF_DIFF_MATCH != result:
                return result
        else:
            return (DEF_DIFF_MATCH if len(self._tokens) == len(other._tokens)
                    else DEF_DIFF_UNIQUE)

    def is_match(self, other):
        return DEF_DIFF_MATCH is self.diff(other)

    def is_unique(self, other):
        return DEF_DIFF_UNIQUE is self.diff(other)

    def is_conflict(self, other):
        return DEF_DIFF_CONFLICT is self.diff(other)


# I still need the subsentence idea for parse modes, unless I go for the
# keyword approach...
class SubSentence(SignatureElement):
    """Repersents a sub-sentence in a function signature.

    :ivar sub_type: The type of the sub-sentence.
        Currently it only exists to make them unique, but we may get things
        from the type later."""

    def __init__(self, sub_type):
        self.sub_type = sub_type

    def __eq__(self, other):
        return self.sub_type == other.sub_type


sub_signature = SubSentence(Signature)
sub_expression = SubSentence(Sentence)

SUBSENTENCE = 'subsentence'
SUBSIGNATURE = 'subsignature'


class MatchPointer:

    def __init__(self, scope):
        self.cur_node = scope._root

    def end(self):
        definition = self.cur_node.defintion
        if definition is None:
            # What to do if there is no definition?
        return definition

    def next(self, token):
        for (t, node) in self.cur_node.tokens:
            if t == token:
                self.cur_node = node
                return
