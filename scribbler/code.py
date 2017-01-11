#!/usr/bin/env python3
"""Repersenting the internal code.

I'm still not sure what this should look like. I'm still figuring it out.

What I need is a way to convert the parse tree into code. The words used to
create the nodes don't actually matter at this point. (Maybe debugging?)
Anyways, I think that these should be enough, until we start adding
immutablity. (Scratch that, does not allow for parameters.)"""


# With duck typing I don't think I actually need this.
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

    def evaluate(self, scope):
        """Evaluate the function."""
        return self.core(arg.evaluate(scope) for arg in self.arg_exs)


class ValueEx(Expression):

    def __init__(self, value):
        """Define an expression that returns a given value."""
        self.value = value

    def evaluate(self, scope):
        """Get the stored value."""
        return self.value


class ParameterEx(Expression):

    def __init__(self, param_number):
        """Define an expression that returns the value of a parameter."""
        self.param_number = param_number

    def evaluate(self, scope):
        """Get the value of the parameter for this call."""
        return scope._some_param_lookup_(self.param_number)
