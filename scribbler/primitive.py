#!/usr/bin/env python3
"""Translating primitives into values. Primitives are not defined, but have
an intrinsic value and type based on the tokens used."""


from base_types import (
    IntegerType,
    )
from scope import (
    Definition,
    )
from tokenization import (
    IntegerToken,
    )


def primitive_integer(sentence):
    value = int(sentence[0].text)
    return Definition(sentence, value, IntegerType())


def primitive_lookup(sentence):
    if not sentence.is_primitive():
        raise Exception('May not translate non-primitive.')
    elif isinstance(sentence[0], IntegerToken):
        return primitive_integer(sentence)
    else:
        raise Exception('Unknown token type. Token: ' + repr(token))
