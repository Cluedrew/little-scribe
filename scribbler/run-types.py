#!/usr/bin/env python3
"""Defines type objects used in Little Scribe."""


class AnythingType:
    """Takes any type"""

    pass


class FunctionType:
    """A callable type which runs code and returns a value.

    All functions are pure (having no side effects) and return exactly one
    value. This may change in later versions."""

    def __init__(self, parameter_types, return_type):
        # Function ... to ...
        self.parameter_types = parameter_types
        self.parameter_count = len(parameter_types)
        self.return_type = return_type


class NumberType:
    """Repersents a value that comes from a NumberToken, positive integers."""


# Planned, not immediate.
class ListType:
    """The basic sequence type."""

    def __init__(self, element_type):
        self.element_type = element_type


# Not as sure about this one:
class UnionType:

    def __init__(self, unioned_types):
        self.unioned_types = unioned_types


#is_subtype(supertype, subtype) -> bool
#common_parent(left_type, right_type) -> new parent
