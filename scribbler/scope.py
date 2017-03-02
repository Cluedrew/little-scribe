#!/usr/bin/env python3
"""This modual defines Scopes and related classes.

This includes the actual Definitions and tools for creating and manuplating
both classes."""


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

    class _Node:
        """Internal class used in constructing a tri, to store definions."""

        def __init__(self)
            self.sub_type = None
            self.sub_node = None
            self.tokens = []
            self.definition = None


DEF_DIFF_MATCH = 'match'
DEF_DIFF_CONFLICT = 'conflict'
DEF_DIFF_UNIQUE = 'unique'


class Definition:
    """A Definition in Little Scribe. Currently only function definitions.

    :ivar pattern: A sequence that repersents the series of tokens used when
        parsing to match this definition.
    :ivar code: Object used to evaluate the function from its arguments.

    [? I think this would be worth it for debugging. ?]
    :ivar name: The full name of the function. Usually the pattern with the
        parameters given.
    [? Currently lacking type system... some day though. ?]
    :ivar type: The function's type, Function <Args> to <Return>.
    """

    def __init__(self, pattern, code):
        self.pattern = pattern
        self.code = code

    @staticmethod
    def from_define(head, body):
        """Create a new function Definition from the Define.

        TODO Eventually this should probably be moved to the modual where the
        built in functions are provided, as it is just a built in, although an
        unusual one.

        :param head: The Sentence that defines the function signature.
        :param body: The Sentence that defines the function body."""
        pattern = []
        iterator = iter(head)
        params = []
        token = next(iterator)
        if not isinstance(token, FirstToken):
            raise Exception('Error: head did not begin with token')
        for token in iterator:
            if isinstance(token, PeriodToken):
                try:
                    iter(iterator)
                except StopIteration:
                    break
                raise Exception('Embedded Period.')
            elif isinstance(token, WordToken):
                pattern.append(token)
            elif isinstance(token, Sentence):
                pattern.append(SUBSENTENCE)
                params.append(token)
        # TODO
        code = some_magic_function(params, body)
        return Definition(pattern, code)

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


SUBSENTENCE = 'subsentence'
SUBSIGNATURE = 'subsignature'


class MatchPointer:

    def __init__(self, scope):
        self.cur_node = scope._root

    def end(self):
        definition = self.cur_node.defintion
        if definition is None:
            raise NoDefinitionError('Is not a match.')
        return definition

    def has_end(self):
        return self.cur_node.definition is not None

    def next(self, token):
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

    def sub_type(self):
        return self.cur_node.sub_type
