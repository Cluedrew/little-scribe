#!/usr/bin/env python3
"""Repersenting the internal code.

I'm still not sure what this should look like. I'm still figuring it out.

What I need is a way to convert the parse tree into code. The words used to
create the nodes don't actually matter at this point. (Maybe debugging?)
Anyways, I think that these should be enough, until we start adding
immutablity. (Scratch that, does not allow for parameters.)"""


class Expression:

    def evaluate(self):
        raise NotImplementedError()


class FunctionEx(Expression):

    def __init__(self, core, arg_exs):
    """Create a new expression from a function.

    :param core: A callable that combines the results of the arguments.
    :param arg_exs: List of argument expressions, that are evaluated to
        produce the inputs to core.
    """
        self.core = core
        self.arg_exs = arg_exs

    def evaluate(self):
    """Evaluate the function."""
    return self.core(arg.evaluate() for arg in self.arg_exs)

class ValueEx(Expression):

    def __init__(self, value):
        """Define an expression that returns a given value."""
        self.value = value

    def evaluate(self):
    """Get the stored value."""
    return self.value
