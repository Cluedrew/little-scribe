#!/usr/bin/env python3
"""Repersenting the internal code.

I'm still not sure what this should look like. I'm still figuring it out.

What I need is a way to convert the parse tree into code. The words used to
create the nodes don't actually matter at this point. (Maybe debugging?)
Anyways, I think that these should be enough, until we start adding
immutablity. (Scratch that, does not allow for parameters.)"""

# I am going full: "Make this up as I go" here. Hopefully I can use that to
# create a working version and refine it later. Or at least have a base.


class FunctionCode:
    """Base class to implement the code behind a Definition."""

    def __call__(self, *args):
       raise NotImplementedError()


class Parameter:
    """A node that evaluates to a parameter of the function."""

   def __init__(self, pos):
       self.pos = pos


class FunctionApplication:
    """A function application is the parsed form of a Sentence.

    This assumes that all of the Sentences have already been bound to their
    values (or replace with a Parameter object) and does not use a Scope to
    find their values itself."""

    def __init__(self, func, args):
        self.func = func
        self.args = args

    def __call__(self, *params):
        evaluated_args = [
            arg.eval(*params) if isinstance(arg, FunctionApplication) else
            params[arg.pos] if isinstance(arg, Parameter) else arg
            for arg in self.args
            ]
        if isinstance(func, Parameter):
            return params[arg.pos](*evaluated_args)
        return func(*evaluated_args)


class ValueNode:
    """A callable that returns the value of a ValueToken."""

    def __init__(self, token):
    if not isinstance(token, ValueToken):
        raise TypeError('ValueNode not given value token.')
    self.val = token.get_value()

    def __call__(self, *params):
        return self.val


class FunctionUserDefined:
    """A user defined function."""

    def __init__(self, application):
        self.app = application

    def __call__(self, *args):
        if isinstance(self.app, FunctionApplication):
            return self.app(*args)
        return self.app


# Built in functions:


def define_function(scope, head, body):
    """Create a new function Definition. Define Head. to be Body. .

    :param head: The Sentence that defines the function signature.
    :param body: The Sentence that defines the function body."""
    # Creating the pattern that defines the function signature.
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
    # Create a subscope of scope with the parameter's defined.
    local_scope = Scope(scope)
    # ...
    # Creating the code for a user defined function.
    code = sentence_to_function_application(local_scope)
    # ? code = FunctionApplication.from_sentence(scope, sentence)
    return Definition(pattern, code)

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

#Definintion([FirstToken('Define'), SUBSIGNATURE, WordToken('to'),
#             WordToken('be'), SUBSENTENCE], define_function)
