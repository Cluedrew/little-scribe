#/usr/bin/env python3

from unittest import (
    TestCase,
    )
from unittest.mock import (
    call,
    patch,
    )

from parse import (
    Parser,
    Sentence,
    TokenStream,
    )
from scope import (
    Scope,
    )
from tokenization import (
    FirstToken,
    PeriodToken,
    Token,
    WordToken,
    )


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

    def test_parse_page(self):
        with patch('parse.Parser.parse_paragraph', side_effect=[1, 2, 3],
                autospec=True) as paragraph_mock:
            with patch('parse.TokenStream.not_empty', autospec=True,
                    side_effect=[True, True, False]) as not_empty_mock:
                parser = fake_parser(['One', 'two'])
                parser.parse_page()
        self.assertEqual(2, paragraph_mock.call_count)
        self.assertEqual(3, not_empty_mock.call_count)

    def test_parse_signature(self):
        # Define New value. to be Five. .
        parser = fake_parser([
            FirstToken('Define'), FirstToken('New'),
            WordToken('value'), PeriodToken('.'), WordToken('to'),
            WordToken('be'), FirstToken('Five'),
            PeriodToken('.'), PeriodToken('.'),
            ])
        sig = parser.parse_signature()
        self.assertIsInstance(sig, Sentence)
        self.assertIsInstance(sig._children[1], Sentence)
        self.assertIsInstance(sig._children[4], Sentence)
        self.assertEqual(sig._children[0].text, 'Define')
        self.assertIsInstance(sig._children[5], PeriodToken)
        self.assertEqual(sig._children[1]._children[0].text, 'New')


class TestTokenStream(TestCase):

    def test_iter_interface(self):
        ts = TokenStream(FakeStream(
            [FirstToken('Test'), WordToken('sentence'), PeriodToken()]))
        self.assertIs(ts, iter(ts))
        self.assertEqual(FirstToken('Test'), next(ts))
        self.assertEqual(WordToken('sentence'), next(ts))
        self.assertEqual(PeriodToken(), next(ts))
        with self.assertRaises(StopIteration):
            next(ts)

    def test_empty(self):
        ts = TokenStream(FakeStream([PeriodToken()]))
        self.assertFalse(ts.is_empty())
        self.assertTrue(ts.not_empty())
        next(ts)
        self.assertTrue(ts.is_empty())
        self.assertFalse(ts.not_empty())

    def test_push_back(self):
        ts = TokenStream(FakeStream([PeriodToken()]))
        ts.push_back(FirstToken('Test'))
        self.assertEqual(FirstToken('Test'), next(ts))
        self.assertEqual(PeriodToken(), next(ts))

    def test_push_back_overload(self):
        ts = TokenStream(FakeStream([]))
        ts.push_back(PeriodToken())
        with self.assertRaises(ValueError):
            ts.push_back(PeriodToken())
