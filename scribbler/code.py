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

# This will not handle
class Parameter:
    """A node that evaluates to a parameter of the function."""

   def __init__(self, pos):
       self.pos = pos

class FunctionApplication:
    """A function application is the parsed form of a sentence. I think."""

    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def __call__(self, *params):
        # A more universal way to handle this might be a Scope.
        evaluated_args = [
            arg.eval(*params) if isinstance(arg, FunctionApplication) else
            params[arg.pos] if isinstance(arg, Parameter) else arg
            for arg in self.args
            ]
        if isinstance(func, Parameter):
            return params[arg.pos](*evaluated_args)
        return func(*evaluated_args)


class FunctionUserDefined:
    """A user defined function."""

    def __init__(self, application):
        self.app = application

    def __call__(self, *args):
        self.app(*args)

# Then we can just have a bunch of functions that repersent the actual
# built in functions.
#
# def define_function(head, body):
#     ...
#
# Definition([FirstToken('Define'), 'SIGNATURE', WordToken('to'),
#             WordToken('be'), 'SIGNATURE'],
#            ['Define', ['Function', 'with', ['Parameters', '.'], '.'],
#             'to', 'be', ['Function', 'body', '.'], '.'],
#            define_function)
# OK, if nothing else I got to figure out what to do about the name (2nd)
# but I think the basic pattern of binding code to names will work.




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
