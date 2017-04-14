#!/usr/bin/env python3
"""Implements REPL, Read Evaluate Print Loop.

This is still a sketch, I have very little idea of what I'm doing."""

def repl(input_file):
    scope = Scope()
    add_build_ins(scope)
    for paragraph in parser.iter_paragraph(scope):
        result = evaluate(paragraph, scope)
        if isinstance(result, Action):
            result.act(scope)
        else:
            print(result)


def evaluate(sentence, scope):
    if sentence.is_primitive():
        return sentence.get_value()
    func = scope.match_sentence(sentence)
    params = []
    for el in sentence:
        if isinstance(el, Sentence):
            params.append(evaluate(el, scope))
    return func(*params)
