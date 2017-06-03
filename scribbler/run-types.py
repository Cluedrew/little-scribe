#!/usr/bin/env python3
"""Defines type objects used in Little Scribe."""


from abc import (
    ABCMeta,
    abstractmethod,
    )


class BaseType(metaclass=ABCMeta):
    """The base type used to create other types."""

    @staticmethod
    @abstractmethod
    def is_super_of(self, other):
        """Checks to see if self repersents a non-strict super type of other."""
        pass


class AnythingType:
    """Takes any type."""

    def is_super_of(self, other):
        """Checks to see if self repersents a non-strict super type of other."""
        return True


# Maybe, I might need this for the first field of Define sentences.
class TextType:
    """Unevaluated sentences."""

    def is_super_of(self, other):
        return isinstance(other, TextType)


class FunctionType:
    """A callable type which runs code and returns a value.

    All functions are pure (having no side effects) and return exactly one
    value. This may change in later versions."""

    def __init__(self, parameter_types, return_type):
        # Function ... to ...
        self.parameter_types = parameter_types
        self.parameter_count = len(parameter_types)
        self.return_type = return_type

    def is_super_of(self, other):
        if not isinstance(other, FunctionType):
            return False
        if not self.parameter_count == other.parameter_count:
            return False
        if not self.return_type.is_super_of(other.return_type):
            return False
        return all(other_pt.is_super_of(self_pt) for (self_pt, other_pt) in
                   zip(self.parameter_types, other.parameter_types))


class NumberType:
    """Repersents a value that comes from a IntegerToken.

    Currently limited to non-negative integers, but that might change."""

    def is_super_of(self, other):
        return isinstance(other, (NumberType, IntegerType))


class IntegerType:

    def is_super_of(self, other):
        return isinstance(other, IntegerType)


# Planned, not immediate.
class ListType:
    """The basic sequence type."""

    def __init__(self, element_type):
        self.element_type = element_type

    def is_super_of(self, other):
        return (isinstance(other, ListType) and
                self.element_type.is_super_of(other.element_type))


# Possibilities:
class UnionType:

    def __init__(self, unioned_types):
        self.unioned_types = unioned_types

    def is_super_of(self, other):
        if isinstance(other, UnionType):
            return all(any(self_option.is_super_of(other_option)
                           for self_option in self.unioned_types)
                       for other_option in other.unioned_types)
        else:
            return any(union_option.is_super_of(other)
                       for union_option in self.unioned_types)


class ExpressionType:

    def __init__(self, result_type):
        self.result_type = result_type

    def is_super_of(self, other):
        return (isinstance(other, ExpressionType) and
                self.result_type.is_super_of(other.result_type))


def is_super(supertype, subtype):
    """Check to see if the first argument is a super type of the second."""
    return supertype.is_super_of(subtype)


def common_parent(left_type, right_type):
    """Find a common parent of the two provided types."""
    return AnythingType()
