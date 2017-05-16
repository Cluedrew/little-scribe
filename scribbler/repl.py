#!/usr/bin/env python3
"""Implements REPL, Read Evaluate Print Loop.

This is still a sketch, I have very little idea of what I'm doing."""


from contextlib import (
    contextmanager,
    )

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
from tokenization import (
    file_token_stream,
    )


def repl_core(input_file, output_file):
    base_scope = create_built_in_scope()
    scope = Scope(base_scope)
    parser = Parser(file_token_stream(input_file))
    for paragraph in parser.iter_paragraph(scope):
        result = evaluate(paragraph, scope)
        if isinstance(result, Action):
            result.do(scope)
        else:
            print(result, file=output_file)


def repl_file(input_file_name, output_file_name):
    with open(input_file_name) as input_file:
        with open(output_file_name) as output_file:
            repl(input_file, output_file)


def repl(input, output):

    @contextmanager
    def force_to_stream(xput, mode='r'):
        if isinstance(xput, str):
            with open(xput, mode) as file:
                yield file
        else:
            yield xput

    with force_to_stream(input, 'r') as input_file:
        with force_to_stream(output, 'w') as output_file:
            repl_core(input_file, output_file)
