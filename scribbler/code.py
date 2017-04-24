#!/usr/bin/env python3
"""Repersenting the internal code.

I'm still not sure what this should look like. I'm still figuring it out.

What I need is a way to convert the parse tree into code. The words used to
create the nodes don't actually matter at this point. (Maybe debugging?)
Anyways, I think that these should be enough, until we start adding
immutablity. (Scratch that, does not allow for parameters.)"""


from itertools import count
from scope import (
    Definition,
    Scope,
    )


def define_function(scope, head, body):
    """Create a new function Definition. 'Define Head. to be Body. .'

    :param scope: The enclosing scope around the definition.
    :param head: The Sentence that defines the function signature.
    :param body: The Sentence that defines the function body."""
    params = []
    for item in head:
        if isinstance(item, Sentence):
            params.append(item)

    def eval_function(args):
        local_scope = Scope(scope)
        for (param, arg) in zip(params, args):
            new_def = Definition.from_sentence(param, arg)
            local_scope.add_definition(new_def)
        return evalutate(body, local_scope)

    return eval_function


define_definition = Definintion(
   [FirstToken('Define'), SUBSIGNATURE,
    WordToken('to'), WordToken('be'), SUBSENTENCE],
   define_function)


def sentence_to_function_application(scope, sentence):
    """Convert a Sentence to a FunctionApplication with the scope."""
    if 1 == len(sentence) and isinstance(sentence[0], ValueToken):
        return ValueNode(sentence[0])
    args = []
    # Note, this has already been matched so it should always match.
    match = scope.new_matcher()
    for el in sentence:
        if isinstance(el, sentence):
            args.append(sentence_to_function_application(scope, el))
            match.next_sub()
        else:
            match.next(el)
    return FunctionApplication(match.end(), args)


def create_built_in_scope():
    """Returns a scope with all the built-in functions defined."""
    scope = Scope()
    scope.add_definition(define_definition)
    scope.add_definition(Definition(
        [FirstToken('Add'), SUBSENTENCE, WordToken('to'), SUBSENTENCE],
        lambda(left, right): left + right))
    scope.add_definition(Definition(
        [FirstToken('Minus'), SUBSENTENCE, WordToken('by'), SUBSENTENCE],
        lambda(left, right): left - right))
    return scope
