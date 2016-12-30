#/usr/bin/env python3

from unittest import (
    TestCase,
    )

from parse import (
    Parser,
    )
from tree import (
    Sentence,
    Token,
    )
#Sentence.children


class FakeStream:

    def __init__(self, tokens):
        self.tokens = tokens
        self.iter = iter(tokens)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.iter)


def fake_parser(tokens):
    return Parser(FakeStream(tokens))


class TestParser(TestCase):

    def _test__next_token(self):
        pass

    def _test__push_back(self):
        pass

    def test__stream_not_empty(self):
        non_empty_stream = fake_parser([Token('period', '.')])
        self.assertTrue(non_empty_stream._stream_not_empty())
        head_stream = fake_parser([])
        head_stream.head = Token('period', '.')
        self.assertTrue(head_stream)
        empty_stream = fake_parser([])
        self.assertFalse(empty_stream._stream_not_empty())

    def _test_parse_signature(self):
        pass
