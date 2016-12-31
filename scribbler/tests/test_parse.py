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
    )
from scope import (
    Scope,
    )
from tree import (
    Paragraph,
    Sentence,
    Token,
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

    def test__next_token(self):
        parser = fake_parser([Token('period', '.')])
        token = parser._next_token()
        self.assertEqual('period', token.kind)
        self.assertEqual('.', token.text)

    def test__push_back(self):
        parser = fake_parser([])
        token = Token('period', '.')
        parser._push_back(token)
        self.assertIs(token, parser.head)
        self.assertIs(token, parser._next_token())

    def test__push_back_overload(self):
        parser = fake_parser([])
        parser._push_back(Token('period', '.'))
        with self.assertRaises(ValueError):
            parser._push_back(Token('word', 'go'))

    def test__stream_not_empty(self):
        non_empty_stream = fake_parser([Token('period', '.')])
        self.assertTrue(non_empty_stream._stream_not_empty())
        head_stream = fake_parser([])
        head_stream._push_back(Token('period', '.'))
        self.assertTrue(head_stream)
        empty_stream = fake_parser([])
        self.assertFalse(empty_stream._stream_not_empty())

    def test_parse_page(self):
        with patch('parse.Parser.parse_paragraph', side_effect=[1, 2, 3],
                autospec=True) as paragraph_mock:
            with patch('parse.Parser._stream_not_empty', autospec=True,
                    side_effect=[True, True, False]) as not_empty_mock:
                parser = fake_parser([])
                parser.parse_page()
        self.assertEqual(2, paragraph_mock.call_count)
        self.assertEqual(3, not_empty_mock.call_count)

    def test_parse_paragraph(self):
        data = [Token('first-word', 'Unit'), Token('period', '.')]
        retval = Sentence(data)
        with patch('parse.Parser.parse_signature', return_value=retval,
                autospec=True) as signature_mock:
            parser = fake_parser([])
            scope = Scope()
            result = parser.parse_paragraph(scope)
        signature_mock.assert_called_once_with(parser)
        self.assertIsInstance(result, Paragraph)
        self.assertIs(result.children, data)

    def test_parse_signature(self):
        # Define New value. to be Five. .
        parser = fake_parser([
            Token('first-word', 'Define'), Token('first-word', 'New'),
            Token('word', 'value'), Token('period', '.'), Token('word', 'to'),
            Token('word', 'be'), Token('first-word', 'Five'),
            Token('period', '.'), Token('period', '.'),
            ])
        sig = parser.parse_signature()
        self.assertIsInstance(sig, Sentence)
        self.assertIsInstance(sig.children[1], Sentence)
        self.assertIsInstance(sig.children[4], Sentence)
        self.assertEqual(sig.children[0].text, 'Define')
        self.assertEqual(sig.children[5].kind, 'period')
        self.assertEqual(sig.children[1].children[0].text, 'New')
