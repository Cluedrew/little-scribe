#!/usr/bin/env python3
"""Defines type objects used in Little Scribe."""


from abc import (
    ABCMeta,
    abstractmethod,
    )


class BaseType(metaclass=ABCMeta):
    """The base type used to create other types."""

    @abstractmethod
    def is_super_of(self, other):
        """Checks to see if self repersents a non-strict super type of other."""
        pass


class AnythingType:
    """Takes any type."""

    def is_super_of(self, other):
        """Checks to see if self repersents a non-strict super type of other."""
        return True


# Maybe: I might need this for the first field of Define sentences.
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
        def any_option_super_of(single):
            return any(self_option.is_super_of(single)
                       for self_option in self.unioned_types)

        if isinstance(other, UnionType):
            return all(any_option_super_of(other_option)
                       for other_option in other.unioned_types)
        else:
            return any_option_super_of(other)


class ExpressionType:

    def __init__(self, result_type):
        self.result_type = result_type

    def is_super_of(self, other):
        return (isinstance(other, ExpressionType) and
                self.result_type.is_super_of(other.result_type))


class StructureType:

    def __init__(self, field_types):
        self.field_types = field_types
        #self.unique_id = new_id()

    def is_super_of(self, other):
        return self is other


class GenericTypeClass:

    def __init__(self):
        # Generic over ... is ... .
        # For all ... define ... .
        # Function over ... taking ... to ... .


def is_super(supertype, subtype):
    """Check to see if the first argument is a super type of the second."""
    return supertype.is_super_of(subtype)


def common_parent(left_type, right_type):
    """Find a common parent of the two provided types."""
    return AnythingType()


# I was going to have special things in the language for types, instead making
# a type called Type and storing types in the global namespace. Then each type
# is an instance that can be referenced, but has a single copy.
# How does this work with type defintions. (... -> Type)

# Type (type of types)
# Anything - Number - Integer - Character - String
# ex. ('Anything.', AnythingType(), type_type)
def type_list():
    lst = []
    type_type = TypeType()
    def append(name, code, type=type_type):
        lst.append(Definition(string_to_signature(name), code, type))

    append('Type.', type_type)
    append('Anything.', AnythingType())
    append('Number.', NumberType())
    append('Integer.', IntegerType())
