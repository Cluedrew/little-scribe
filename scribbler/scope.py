#!/usr/bin/env python3
"""This modual defines Scopes and related classes.

This includes the actual Definitions and tools for creating and manuplating
both classes."""


import sys
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
        for el in definition.pattern:
            if isinstance(el, Token):
                for t,n in node.tokens:
                    if t == el:
                        node = n
                        break
                else:
                    new_node = Scope._Node()
                    node.tokens.append( (el, new_node) )
                    node = new_node
            elif el is SUBSENTENCE or el is SUBSIGNATURE:
                if node.sub_type is el:
                    node = node.sub_node
                elif node.sub_type is None:
                    node.sub_type = el
                    node.sub_node = Scope._Node()
                    node = node.sub_node
                else:
                    raise ScopeFault('New definition would conflict.')
            else:
                raise ScopeFault('Bad element in new definition.')
        else:
            if node.definition is not None:
                raise ScopeFault('New definition would conflict.')
            node.definition = definition

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


# TRYING THIS OUT
class FunctionScope(Scope):
    """A sub-scope for use within a function. (Something, it is a mess.)"""

    def __init__(self, parent, signature):
        super(FunctionScope, self).__init__(parent)
        self.signature = signature
        self.func = Definition.from_sentence(signature, 'This function')
        self.params = []
        for element in signature:
            if isinstance(element, Sentence):
                self.add_definition(Definition.from_sentence(element, None)

    def apply(self, *args):
        sub = FunctionScope(self._parent, self.signature)
        sub._apply(*args)

    def _apply(self, *args):
        for (index, param) in enumerate(self.params):
            param.code = args[index]


DEF_DIFF_MATCH = 'match'
DEF_DIFF_CONFLICT = 'conflict'
DEF_DIFF_UNIQUE = 'unique'


class Definition:
    """A Definition in Little Scribe, a name bound to a value.

    :ivar pattern: A sequence that repersents the series of tokens used when
        parsing to match this definition.
    :ivar code: Object used to evaluate the function from its arguments.

    This should be expanded in later versions. But I think this is the
    minimum required to get it working.
    """

    def __init__(self, pattern, code, type=None):
        self.pattern = pattern
        self.code = code
        self.type = type
        self._scope = None

    @staticmethod
    def from_sentence(sentence, code):
        """Short cut, create a definition pattern from a sentence.

        The pattern uses all SUBSENTENCE values and strips the dot."""
        if sentence.is_primitive():
            raise ValueError('Definition.from_sentence: '
                'May not define primitive sentence.')
        pattern = []
        for (pos, item) in enumerate(sentence):
            if isinstance(item, PeriodToken):
                if pos < len(sentence) - 1:
                    raise ValueError('Definition.from_sentence: '
                        'Sentence with embedded period.')
                return Definition(pattern, code)
            elif isinstance(item, FirstToken) and 0 != pos:
                raise ValueError('Definition.from_sentence: '
                    'Sentence with embedded first word.')
            elif isinstance(item, Token):
                pattern.append(item)
            elif isinstance(item, Sentence):
                pattern.append(SUBSENTENCE)
        raise ValueError('Definition.from_sentence: Sentence untermainated.')

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

    def enclosing_scope(self):
        return self._scope


SUBSENTENCE = 'subsentence'
SUBSIGNATURE = 'subsignature'


class MatchPointer:

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

    def next(self, element):
        self.next_token(element)

    #def next(self, element):
    #    if isinstance(element, Token):
    #        self.next_token(element)
    #    elif isinstance(element, Sentence):
    #        self.next_sub()
    #    else:
    #        raise TypeError('MatchPointer.next') ~$!

    def sub_type(self):
        return self.cur_node.sub_type
