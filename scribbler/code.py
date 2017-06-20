#!/usr/bin/env python3
"""Repersenting the internal code of Little Scribe and runtime tools.

Built-ins are created simply by adding a Definition to the a scope. Use
`create_built_in_scope` to get an instance of this scope."""

from parse import (
    string_to_signature,
    )
from primitive import (
    primitive_lookup,
    )
from scope import (
    Definition,
    Scope,
    )


class LSRunningError(Exception):
    """Exception type for errors thrown by."""
    # In the future should be replaced by or hiddened behind a Little Scribe
    # error message.

class Action:

    def do(self, scope):
        raise NotImplementedError('Base Action is not to be used.')


def evaluate(sentence, scope):
    """Evaluate a Sentence within a Scope."""
    if sentence.is_primitive():
        return primitive_lookup(sentence).code
    match = scope.match_sentence(sentence)
    params = []
    # Define disables pre-evaluation.
    if sentence[0].text == 'Define':
        for item in sentence.iter_sub():
            params.append(item)
        return match.code(scope, *params)
    # All other functions take the results of their arguments,
    # not the arguments themselves.
    else:
        for item in sentence.iter_sub():
            params.append(evaluate(item, scope))
        # TODO: I need a better divide than this.
        # If there are no arguments, don't evaluate.
        if 0 == len(params):
            return match.code
        # Pass in the scope for user defined functions.
        return match.code(scope, *params)


# TODO: currently actually the general define for both values and functions.
def define_function(scope, head, body):
    """Create a new function Definition. 'Define Head. to be Body. .'

    :param scope: The enclosing scope around the definition.
    :param head: The Sentence that defines the function signature.
    :param body: The Sentence that defines the function body."""
    params = []
    for item in head.iter_sub():
        params.append(item)

    if 0 == len(params):
        return AddDefAction(Definition(head, body))

    def eval_function(scope, *args):
        if len(args) != len(params):
            raise LSRunningError('Incorrect number of arguments. expected: ' +
                str(len(params)) + ' actual: ' + str(len(args)))
        local_scope = Scope(scope)
        for (param, arg) in zip(params, args):
            new_def = Definition(param, arg)
            local_scope.add_definition(new_def)
        # Head should be defined in the parent scope.
        return evaluate(body, local_scope)

    #anything = little_scribe_types['anything']
    #ftype = FunctionType([anything] * len(params), anything)

    return AddDefAction(Definition(head, eval_function))


def define_constant(scope, head, body):
    """Define a new immutable value.

    Currently values may not have fields."""
    for _ in head.iter_sub():
        raise Exception('define_constant: Does not accept fields.')
    return AddDefAction(Definition(head, evaluate(body, scope)))


def define__unspecified(scope, head, body):
    """Define something based on the contents of head."""
    for _ in head.iter_sub():
        return define_function(scope, head, body)
    return define_constant(scope, head, body)


class AddDefAction(Action):

    def __init__(self, definition):
        self.definition = definition

    def do(self, scope):
        scope.add_definition(self.definition)


# Should this be here?
class ListObject:

    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def to_under_list(self):
        """Convert this to a python list."""
        return [self.head] + self.tail.to_under_list()


class EmptyList:

    def to_under_list(self):
        """Convert this to a python list."""
        return list()


def create_built_in_scope():
    """Returns a scope with all the built-in functions defined."""
    scope = Scope()

    def add_text(text, code, type=None):
        scope.add_definition(Definition(string_to_signature(text), code, type))

    #for definition in create_type_list():
    #    scope.add_definition(definition)
    add_text('Define Head. to be Body. .', define_function)
    add_text('Add Left hand side. to Right hand side. .',
        lambda scope, left, right: left + right)
    add_text('Minus Left hand side. by Right hand side. .',
        lambda scope, left, right: left - right)

    add_text('Put Head. onto Tail. .',
        lambda scope, head, tail: ListObject(head, tail))
    add_text('Head of List. .', lambda scope, list: list.head)
    add_text('Tail of List. .', lambda scope, list: list.tail)
    add_text('Empty list.', EmptyList())
    add_text('Is This value. empty.',
        lambda scope, value: isinstance(value, EmptyList))
    return scope
