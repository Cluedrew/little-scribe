#!/usr/bin/env python3
"""Repersenting the internal code of Little Scribe and runtime tools.

Built-ins are created simply by adding a Definition to the a scope. Use
`create_built_in_scope` to get an instance of this scope."""

from parse import (
    string_to_signature,
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
        return sentence.get_value()
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
        # TODO: The scope might be unneeded in this case, figure that out.
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


def create_built_in_scope():
    """Returns a scope with all the built-in functions defined."""
    scope = Scope()

    def add_text_definition(text, code, type=None):
        scope.add_definition(Definition(string_to_signature(text), code, type))

    scope.add_definition(Definition(
        string_to_signature('Define Head. to be Body. .'), define_function))
    scope.add_definition(Definition(
        string_to_signature('Add Left hand side. to Right hand side. .'),
        lambda scope, left, right: left + right))
    scope.add_definition(Definition(
        string_to_signature('Minus Left hand side. by Right hand side. .'),
        lambda scope, left, right: left - right))
    return scope
