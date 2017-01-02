#!/usr/bin/env python3
"""Testing tools for Scribbler."""

from tokenise import token_regexes


def new_token(text):
    """Return a Token from the string.

    The string must be a valid token. Its kind is derived from the matching
    pattern."""
    for name, pattern in token_regexes:
        if pattern.fullmatch(text):
            return Token(name, text)
    else:
        raise ValueError('No token pattern match for: ' + text)
