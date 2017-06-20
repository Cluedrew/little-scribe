#!/usr/bin/env python3
"""Defines type objects used in Little Scribe."""


from abc import (
    ABCMeta,
    abstractmethod,
    )


from parse import (
    string_to_signature,
    )
from scope import (
    Definition,
    )

class LittleScribeType(metaclass=ABCMeta):
    """The base type used to create other types."""

    @abstractmethod
    def is_super_of(self, other):
        """Checks to see if self repersents a non-strict super type of other."""
        pass


class TypeType(LittleScribeType):

    def is_super_of(self, other):
        return isinstance(other, BaseType)


class AnythingType(LittleScribeType):
    """Takes any type."""

    def is_super_of(self, other):
        """Checks to see if self repersents a non-strict super type of other."""
        return True


# Maybe: I might need this for the first field of Define sentences.
class TextType(LittleScribeType):
    """Unevaluated sentences."""

    def is_super_of(self, other):
        return isinstance(other, TextType)


class FunctionType(LittleScribeType):
    """A callable type which runs code and returns a value.

    All functions are pure (having no side effects) and return exactly one
    value. This may change in later versions."""

    def __init__(self, parameter_types, return_type):
        # Function ... to ...
        self.parameter_types = parameter_types
        self.parameter_count = len(parameter_types)
        self.return_type = return_type

    def is_super_of(self, other):
        return (isinstance(other, FunctionType) and
                self.parameter_count == other.parameter_count and
                self.return_type.is_super_of(other.return_type) and
                all(other_pt.is_super_of(self_pt) for (self_pt, other_pt) in
                    zip(self.parameter_types, other.parameter_types)))

    @staticmethod
    def make(parameter_types, return_type):
        return FunctionType(parameter_types, return_type)


class ListType(LittleScribeType):
    """The basic sequence type."""

    def __init__(self, element_type):
        self.element_type = element_type

    def is_super_of(self, other):
        return (isinstance(other, EmptyType) or
                isinstance(other, ListType) and
                self.element_type.is_super_of(other.element_type))

    @staticmethod
    def make(element_type):
        return ListType(element_type)


class EmptyType(LittleScribeType):
    """Empty sequence value."""

    def is_super_of(self, other):
        return isinstance(other, EmptyType)


class NumberType(LittleScribeType):
    """Repersents a value that comes from a IntegerToken.

    Currently limited to non-negative integers, but that might change."""

    def is_super_of(self, other):
        return isinstance(other, (NumberType, IntegerType))


class IntegerType(NumberType):

    def is_super_of(self, other):
        return isinstance(other, IntegerType)


# Possibilities:
class UnionType(LittleScribeType):

    def __init__(self, unioned_types):
        self.unioned_types = unioned_types

    def is_super_of(self, other):
        def any_option_super_of(single):
            return any(self_option.is_super_of(single)
                       for self_option in self.unioned_types)

        if isinstance(other, UnionType):
            return all(any_option_super_of(other_option)
                       for other_option in other.unioned_types)
        else:
            return any_option_super_of(other)


class ExpressionType(LittleScribeType):

    def __init__(self, result_type):
        self.result_type = result_type

    def is_super_of(self, other):
        return (isinstance(other, ExpressionType) and
                self.result_type.is_super_of(other.result_type))


class StructureType(LittleScribeType):

    def __init__(self, field_types):
        self.field_types = field_types
        #self.unique_id = new_id()

    def is_super_of(self, other):
        return self is other


def is_super(supertype, subtype):
    """Check to see if the first argument is a super type of the second."""
    return supertype.is_super_of(subtype)


def common_parent(left_type, right_type):
    """Find a common parent of the two provided types."""
    return AnythingType()


type_type = TypeType()


def type_def(text, code, type=type_type):
    return Definition(string_to_signature(text), code, type)


little_scribe_types = {
    'type': type_def('Type.', type_type),
    'anything': type_def('Anything.', AnythingType()),
    'number': type_def('Number.', NumberType()),
    'integer': type_def('Integer.', IntegerType()),
    #'function': type_def('Function Parameter list, to Return type. .',
    #    FunctionType.make,
    #    FunctionType([ListType.make(type_type)], type_type)),
    #'list': type_def('List of Item type. .',
    #    ListType.make, FunctionType([type_type], type_type)),
    }
