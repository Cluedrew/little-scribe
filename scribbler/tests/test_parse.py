#!/usr/bin/env python3

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
    string_to_signature,
    TokenStream,
    )
from scope import (
    Definition,
    Scope,
    )
from tokenization import (
    FirstToken,
    PeriodToken,
    Token,
    tokenify_list,
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

    def test_iter_paragraph(self):
        scope = Scope()
        with patch('parse.Parser.parse_paragraph', side_effect=[1, 2, 3],
                autospec=True) as paragraph_mock:
            with patch('parse.TokenStream.not_empty', autospec=True,
                    side_effect=[True, True, False]) as not_empty_mock:
                parser = fake_parser(['One', 'two'])
                for paragraph in parser.iter_paragraph(scope):
                    pass
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

    def make_test_scope(self):
        scope = Scope()
        scope.add_definition(Definition(string_to_signature('Unit.'), 0))
        scope.add_definition(Definition(
            string_to_signature('Something with Sub sentence. to parse.'), 1))
        scope.add_definition(Definition(
            string_to_signature('Define New thing. to be a new type.'), 2))
        return scope

    def test_parse_expression(self):
        scope = self.make_test_scope()
        parser = fake_parser(tokenify_list(['Something', 'with', 'Unit', '.',
            'to', 'parse', '.']))
        exp = parser.parse_expression(scope)
        self.assertEqual(exp,
            string_to_signature('Something with Unit. to parse.'))

    def test_parse_expression_with_value(self):
        scope = self.make_test_scope()
        tokens = tokenify_list(['Something', 'with', '5', 'to', 'parse', '.'])
        parser = fake_parser(tokens)
        exp = parser.parse_expression(scope)
        self.assertEqual(exp,
            Sentence(tokens[0:2] + [Sentence(tokens[2])] + tokens[3:]))

    def test_parse_expression_dispatch_to_definition(self):
        scope = self.make_test_scope()
        parser = fake_parser(tokenify_list(['Define', 'Sig', 'sentence', '.',
            'to', 'be', 'a', 'new', 'type', '.']))
        with patch.object(parser, 'parse_definition') as mock_parse_def:
             parser.parse_expression(scope)
        mock_parse_def.assert_called_once_with(scope)

    def test_parse_definition(self):
        scope = self.make_test_scope()
        parser = fake_parser(tokenify_list(['Define', 'Sig', 'sentence', '.',
            'to', 'be', 'a', 'new', 'type', '.']))
        dfn = parser.parse_definition(scope)
        self.assertEqual(dfn,
            string_to_signature('Define Sig sentence. to be a new type.'))


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


class TestStringToSignature(TestCase):

    def test_flat_signature(self):
        result = string_to_signature('Frames per second.')
        self.assertEqual(FirstToken('Frames'), result[0])
        self.assertEqual(WordToken('per'), result[1])
        self.assertEqual(WordToken('second'), result[2])
        self.assertEqual(PeriodToken(), result[3])

    def test_nested_signature(self):
        result = string_to_signature('Define Head. to be Body. .')
        self.assertEqual(FirstToken('Head'), result[1][0])
        self.assertEqual(PeriodToken(), result[1][1])
        self.assertEqual(WordToken('to'), result[2])
