#!/usr/bin/env python3
"""Actions allow functions to have effects.

If a Action is returned by a paragraph-level Sentence it will be executed on
the scope."""


class Action:
    """Stub definition for base Action."""

    def act(self, scope):
        NotImplementedError()


class AddDefinitionAction(Action):
    """Add a Definition to the scope."""

    def __init__(self, definition):
        self.definition = definition

    def act(self, scope):
        scope.add_definition(self.definition)
