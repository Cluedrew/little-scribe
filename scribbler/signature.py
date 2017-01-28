#!/usr/bin/env python3
"""Modual for defining Signatures for function definitions.

It also defines the SignatureElement, which must be used to fill the
Signature and SubSentence which..."""


# Constants returned by the diff function.
# MATCH: Equal, there is no difference between the Signatures.
SIG_DIFF_MATCH = 'match'
# UNIQUE: There is a visible difference between the two.
SIG_DIFF_UNIQUE = 'unique'
# CONFLICT: These is a difference that cannot be seen while parsing.
SIG_DIFF_CONFLICT = 'conflict'


# Can I make this hashable? If I can make SignatureElement hashable,
# then I should be able to store the signature elements in a tuple.

# OK, another issue, this signature for matching is actually different
# from the Signature we read in while parsing.
class Signature:
    """A signature is a list that repersents the signature of a sentence.

    It is 'immutable' in that set operations are made inconvenent. And some
    simple type checks are performed. Other than that it is a convence
    wrapper."""

    def __init__(self, init):
        self._tokens = tuple(init)
        for token in self._tokens:
            if not isinstance(token, SignatureElement):
                raise TypeError('Invalid Signature value')

    def __len__(self):
        return len(self._tokens)

    def __iter__(self):
        return iter(self._tokens)

    def __getitem__(self, index):
        return self._tokens[index]

    def diff(self, other):
        """Get the level of difference between two signatures."""
        if not isinstance(other, Signature):
            raise TypeError('diff: other is not a Signature')
        for (self_element, other_element) in zip(self._tokens, other._tokens):
            result = self_element.diff(other_element)
            if SIG_DIFF_MATCH != result:
                return result
        else:
            return (SIG_DIFF_MATCH if len(self._tokens) == len(other._tokens)
                    else SIG_DIFF_UNIQUE)

    def is_match(self, other):
        return SIG_DIFF_MATCH is self.diff(other)

    def is_unique(self, other):
        return SIG_DIFF_UNIQUE is self.diff(other)

    def is_conflict(self, other):
        return SIG_DIFF_CONFLICT is self.diff(other)


class SignatureElement:
    """An interface for elements that can be used inside a signature.

    Implementing classes must define equality.
    All classes that repersent a piece of text should also be children of
    Token, while no classes that repersent a subsentence should."""

    def diff(self, other):
        """Compare two signature elements for their level of difference."""
        if not isinstance(other, SignatureElement):
            raise TypeError('diff: other is not a SignatureElement')
        # This is dependant on the rules of matching, still not worked out.
        are_sub_sentences = [
            isinstance(self, SubSentence), isinstance(other, SubSentence)]
        if all(are_sub_sentences):
            return SIG_DIFF_MATCH if self == other else SIG_DIFF_CONFLICT
        if any(are_sub_sentences):
            return SIG_DIFF_UNIQUE
        return SIG_DIFF_MATCH if self == other else SIG_DIFF_UNIQUE

    def __eq__(self, other):
        raise NotImplementedError()


class SubSentence(SignatureElement):
    """Repersents a sub-sentence in a function signature.

    :ivar sub_type: The type of the sub-sentence.
        Currently it only exists to make them unique, but we may get things
        from the type later."""

    def __init__(self, sub_type):
        self.sub_type = sub_type

    def __eq__(self, other):
        return self.sub_type == other.sub_type


sub_signature = SubSentence(Signature)
sub_expression = SubSentence(Sentence)
