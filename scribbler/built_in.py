#!/usr/bin/env python3
"""Built in sentences for Little Scribe/Scribbler.

As Scribbler follows the language definition of Little Scribe, or is, those
are almost the same thing.

These are the body's of the definitions."""


import scope

def define_function_body(sig, exp):
    """Define the signature to repersent the expression."""
    # I think I don't actually do that here, but return something that does?
    def inner(scope):
        # Add Definition(sig, exp) too scope
    return inner

define_function = Definition(
    [Token('first-word', 'Define'), sub_signature, Token('word', 'to'),
     Token('word', 'be'), sub_experssion], define_function_body)
