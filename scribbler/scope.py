#!/usr/bin/env python3
"""This modual defines Scopes and related classes.

This includes the actual Definitions and tools for creating and manuplating
both classes."""


import enum
import itertools
import sys

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
        return Scope.Matcher(self._build_scope_list())

    def _build_scope_list(self):
        """Return a list of all scopes visible in this scope."""
        scope_list = []
        if self._parent:
            scope_list = self._parent._build_scope_list()
        scope_list.append(self)
        return scope_list

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
        for item in sentence:
            if isinstance(item, PeriodToken):
                break
            elif isinstance(item, Token):
                ptr.next(item)
            else:
                ptr.next()
        if ptr.has_end():
            return ptr.has_end()
        raise NoDefinitionError('Sentence has no match in scope: \'' +
            str(sentence) + "'")

    def new_define_scope(self, signature):
        """Make a subscope as required by the Define keyword."""
        inner_scope = Scope(self)
        for sentence in itertools.chain([signature], signature.iter_sub()):
            inner_scope.add_definition(Definition(sentence, None))
        return inner_scope

    class _Node:
        """Internal class used in constructing a tri, to store definions."""

        def __init__(self):
            self.sub_node = None
            self.tokens = []
            self.definition = None

        def print_tree(self, level=None, link=None, file=sys.stdout):
            next_level = (0 if level is None else level + 1)
            if link is not None:
                cargo = ("" if self.definition is None else ' <def>')
                print((' ' * level) + str(link) + cargo, file=file)
            if self.sub_node is not None:
                self.sub_node.print_tree(next_level, '(SUB)', file=file)
            for (token, node) in self.tokens:
                node.print_tree(next_level, token, file=file)

    class Matcher:
        """Goes through a scope's tri looking for a match."""

        def __init__(self, scope_list):
            self._nodes = [scope._root for scope in scope_list]

        def next(self, element=Sentence()):
            """If element does continue the match, advance.

            :return: True if Matcher advanced, false otherwise."""
            new_nodes = []
            if isinstance(element, Sentence):
                for node in self._nodes:
                    if node.sub_node:
                        new_nodes.append(node.sub_node)
            elif isinstance(element, Token):
                for node in self._nodes:
                    for (token, sub_node) in node.tokens:
                        if element == token:
                            new_nodes.append(sub_node)
                            break
            else:
                raise TypeError('Scope.Matcher.next: element unknown type.')
            if len(new_nodes):
                self._nodes = new_nodes
                return True
            return False

        def has_end(self):
            """Check if a match ends here.

            :return: Matched Definition if there is one, otherwise None.
            Definitions are always true, so this is also a predicate."""
            for node in self._nodes:
                if node.definition:
                    return node.definition
            return None

    def print_list(self, file=sys.stdout):
        """Print out the list of Definitions in the Scope."""
        for define in self._definitions:
            print(define.name, file=file)

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
