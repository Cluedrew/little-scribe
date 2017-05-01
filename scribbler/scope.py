#!/usr/bin/env python3
"""This modual defines Scopes and related classes.

This includes the actual Definitions and tools for creating and manuplating
both classes."""


import enum
import sys
# Would be circlular:
#from parse import (
#    string_to_signature,
#    )
from sentence import (
    Sentence,
    )
from tokenization import (
    PeriodToken,
    Token,
    )

class NoDefinitionError(Exception):
    """No definition where a definition (or a group) was expected."""

class ScopeFault(Exception):
    """Internal Error: Scope is behaving inconsistantly."""


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

    def new_matcher(self):
        """Return an object that can be used to match definitions."""
        return MatchPointer(self)

    def _iter_definitions(self):
        for definition in self._definitions:
            yield definition
        if self._parent is not None:
            for definition in self._parent._iter_definitions():
                yield definition

    def _add_to_tree(self, definition):
        node = self._root
        for item in definition.name:
            if isinstance(item, PeriodToken):
                break
            elif isinstance(item, Token):
                for t,n in node.tokens:
                    if t == item:
                        node = n
                        break
                else:
                    new_node = Scope._Node()
                    node.tokens.append( (item, new_node) )
                    node = new_node
            elif isinstance(item, Sentence):
                if node.sub_node is None:
                    node.sub_node = Scope._Node()
                node = node.sub_node
            else:
                raise ScopeFault('Sentence with illegial child type.')
        if node.definition is not None:
            raise ScopeFault('New definition would conflict.')
        node.definition = definition

    def add_definition(self, definition):
        """Add a new definition to the scope.

        It must not conflict with any existing definition in the scope."""
        for existing in self._iter_definitions():
            if existing.is_conflict(definition):
                raise ValueError('New definition conflicts with existing '
                                 'definition in scope.')
        else:
            self._definitions.append(definition)
            self._add_to_tree(definition)
            definition._scope = self

    def merge(self, other):
        """Merge another Scope into this one."""
        # I don't think I want to handle merging this way.
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

    def match_sentence(self, sentence):
        """Get the definition that matches the Sentence."""
        ptr = self.new_matcher()
        try:
            for el in sentence:
                if isinstance(el, PeriodToken):
                    break
                elif isinstance(el, Token):
                    ptr.next(el)
                else:
                    ptr.next_sub()
            if ptr.has_end():
                return ptr.end()
        except NoDefinitionError:
            raise
        raise NoDefinitionError('Sentence has no match in scope.')

    class _Node:
        """Internal class used in constructing a tri, to store definions."""

        def __init__(self):
            self.sub_type = None
            self.sub_node = None
            self.tokens = []
            self.definition = None

        def print_tree(self, level=0, link=None, file=sys.stdout):
            if link is not None:
                print((' ' * level) + str(link) +
                      (' <def>' if self.definition is not None else ''),
                      file=file)
            if self.sub_type is not None:
                self.sub_node.print_tree(level + 1, self.sub_type, file=file)
            for (token, node) in self.tokens:
                node.print_tree(level + 1, token, file=file)

    def print_definitions(self, file=sys.stdout):
        """Print out the Definition.patterns in the Scope."""
        for define in self._definitions:
            print(str(define.pattern), file=file)

    def print_tree(self, file=sys.stdout):
        """Print out the tree of _Nodes in the tree."""
        self._root.print_tree(file=file)


@enum.unique
class Def_Diff(enum.Enum):
    MATCH = 0
    CONFLICT = 1
    UNIQUE = 2

DEF_DIFF_MATCH = 'match'
DEF_DIFF_CONFLICT = 'conflict'
DEF_DIFF_UNIQUE = 'unique'


class Definition:
    """A Definition in Little Scribe, a name bound to a value.

    :ivar name: A Sentence to match against, it is what the definition
        is for and is matched against.
    :ivar code: Object used to evaluate the function from its arguments.

    This should be expanded in later versions. But I think this is the
    minimum required to get it working.
    """

    def __init__(self, name, code, type=None):
        self.name = name
        self.code = code
        self.type = type

    #@staticmethod
    #def from_text(text, code, type=None):
    #    """Create the Definition name from text."""
    #    return Definition(string_to_signature(text), code, type)

    @staticmethod
    def _diff_element(self_el, other_el):
        """Difference level between two elements of a definition signature."""
        are_tokens = [
            isinstance(self_el, Token), isinstance(other_el, Token)]
        if all(are_tokens):
            return DEF_DIFF_MATCH if self_el == other_el else DEF_DIFF_UNIQUE
        if any(are_tokens):
            return DEF_DIFF_UNIQUE
        return DEF_DIFF_MATCH

    def diff(self, other):
        """Get the level of difference between two definitions."""
        if not isinstance(other, Definition):
            raise TypeError('Definition.diff: other is not a Definition.')
        for (mine, yours) in zip(self.name, other.name):
            result = self._diff_element(mine, yours)
            if DEF_DIFF_MATCH != result:
                return result
        else:
            return (DEF_DIFF_MATCH if len(self.name) == len(other.name)
                    else DEF_DIFF_UNIQUE)

    def is_match(self, other):
        return DEF_DIFF_MATCH is self.diff(other)

    def is_unique(self, other):
        return DEF_DIFF_UNIQUE is self.diff(other)

    def is_conflict(self, other):
        return DEF_DIFF_CONFLICT is self.diff(other)


class MatchPointer:
    """Helper to match a Sentence within a scope."""
    # It might be worth compressing this to next and end.
    # Maybe everything returns instead of using NoDefinitionError.
    # Also, I need a list of nodes, for nested scopes.

    def __init__(self, scope):
        self.cur_node = scope._root

    def end(self):
        definition = self.cur_node.definition
        if definition is None:
            raise NoDefinitionError('Is not a match.')
        return definition

    def has_end(self):
        return self.cur_node.definition is not None

    def next_token(self, token):
        for (t, node) in self.cur_node.tokens:
            if t == token:
                self.cur_node = node
                return
        else:
            raise NoDefinitionError('No possible matches.')

    def next_sub(self):
        if self.cur_node is not None:
            self.cur_node = self.cur_node.sub_node
        else:
            raise NoDefinitionError('No possible matches.')

    def next(self, element=Sentence()):
        """Match a bit more of the Sentence."""
        if isinstance(element, Token):
            self.next_token(element)
        elif isinstance(element, Sentence):
            self.next_sub()
        else:
            raise TypeError('MatchPointer.next: element has invalid type.')

    def try_next(self, element=Sentence()):
        """Try to match more of the Sentence, return success."""
        try:
            self.next(element)
            return True
        except NoDefinitionError:
            return False
