#!/usr/bin/env python3
"""Implements REPL, Read Evaluate Print Loop.

This is still a sketch, I have very little idea of what I'm doing."""


from code import (
    Action,
    create_built_in_scope,
    evaluate,
    )
from parse import (
    Parser,
    )
from scope import (
    Scope,
    )


def repl(input_file):
    base_scope = create_built_in_scope()
    scope = Scope(base_scope)
    parser = Parser()
    for paragraph in parser.iter_paragraph(scope):
        result = evaluate(paragraph, scope)
        if isinstance(result, Action):
            result.do(scope)
        else:
            print(result)


def repl_file(input_file_name):
    with open(input_file_name) as file:
        repl(file)
