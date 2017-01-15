#!/usr/bin/env python3


class Scope:
    """Repersents a collection of definitions in Little Scribe."""

    def __init__(self, parent=None):
        """Create a new scope.

        :param parent: If this is a top level scope, parent should be None,
            if not than it should be another scope instance, repersenting
            the lowest level scope this one is nested within."""
        if parent is not None and not isinstance(parent, Scope):
            raise TypeError("Scope's parent must be None or another Scope.")
        self._parent = parent
        # Currently this list is unsorted, maybe sorting to drop some
        # O(n) operations down to O(logn).
        self._definitions = []

    def _iter_definitions(self):
        for definition in self._definitions:
            yield definition
        if self._parent is not None:
            for definition in self._parent._iter_definitions():
                yield definition

    def add_definition(self, definition):
        """Add a new definition to the scope.

        It must not conflict with any existing definition in the scope."""
        for existing in self._iter_definitions():
            if existing.has_conflict(definition):
                raise ValueError('New definition conflicts with existing '
                                 'definition in scope.')
        else:
            self._definitions.append(definition)

    def merge(self, other):
        """Merge another Scope into this one."""
        # Weak exception garenty.
        for definition in other._iter_definitions():
            for existing in self._iter_definitions():
                if existing is definition:
                    break
                if existing.has_conflicts(definition):
                    raise ValueError('Conflicting definitions in merging '
                                     'scopes.')
            else:
                # This is adding to the same list its reading from.
                self._definitions.append(definition)

    def match_first(self, first_word):
        """Match definitions that start with first_word."""
        group = DefinitionMatchGroup([first_word])
        for definition in self._definitions:
            if first_word == definition[0]:
                group.matching.append(definition)
        return group

    def match_prefix(self, prefix):
        """Match definitions that start with prefix."""
        group = DefinitionMatchGroup(prefix)
        for definition in self._definitions:
            for i in range(len(prefix)):
                if prefix[i] != definition[i]:
                    break
            else:
                group.matching.append(definition)
        return group

    def match_to_end(self, sentence):
        """Match definitions that start with prefix up to the period.

        [The period might become optional at some point.]"""
        has_period = (isinstance(sentence[-1], Token) and
                      sentence[-1].kind == 'period')
        # Go through every definition.
        for definition in self._definitions:
            # Search for a mismatch.
            for (i, word) in enumerate(definition):
                if word is sub_expression:
                    if not isinstance(sentence[i], Sentence):
                        break
                elif isinstance(word, Token):
                    if (word.kind != sentence[i].kind or
                            word.text != sentence[i].text):
                        break
            else:
                return DefinitionMatchGroup(sentence, definition)
        else:
            return DefinitionMatchGroup(sentence)


class SubSentence:
    """Repersents a sub-sentence in a function signature."""

    def __init__(self, value):
        self.value = value


sub_signature = SubSentence(True)
sub_expression = SubSentence(False)


class Definition:
    """Repersents a function definition in Little Scribe.

    A function definition consists of the pattern being defined (the
    Signature) and what it is being defined to (the body)."""

    def __init__(self, signature, body):
        """Create the definition from its signature and the code body.

        :param signature: A list that repersents the signature.
        :param body: A callable that repersents the operation the definition
            preforms on its parameters."""
        self.sig = signature
        self.body = body

    def __call__(self, args):
        """Evaluate the function for a given set of arguments."""
        return self.body(args)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.sig[index]
        else:
            raise TypeError()

    def has_conflict(self, other):
        for i in range(min(len(self.sig), len(other.sig))):
            if self.sig[i] == other.sig[i]:
                continue
            if ((self.sig[i] == sub_expression and
                 other.sig[i] == sub_signature) or
                (self.sig[i] == sub_signature and
                 other.sig[i] == sub_expression)):
                return True
            return False
        else:
            return len(self.sig) == len(other.sig)


class DefinitionMatchGroup:
    """A group of definitions that match a given prefix."""

    def __init__(self, prefix, matching=None):
        self.prefix = prefix
        self.matching = matching if matching is not None else []

    def next_match(self, word):
        """Create a new group that matches a subset of this group.

        The Definitions that match prefix + [word] are matched."""
        at = len(self.prefix)
        new_matching = []
        for index, match in self.matching:
            if match[at] == word:
                new_matching.append(self.matching[index])
        return DefinitionMatchGroup(new_matching, self.prefix + [word])

    def cur_sub_sentence_type(self):
        """Get the type of sub-sentence to be parsed after matching prefix."""
        sentence_type = None
        place = len(self.prefix)
        for definition in self.matching:
            if isinstance(definition[at], SubSentence):
                if sentence_type is None:
                    sentence_type = definition[at]
                elif sentence_type != definition[at]:
                    raise Exception('Conficting SubSentence type: '
                                    'Improper DefinitionMatchGroup')
        return sentence_type

    def __len__(self):
        return len(self.matching)

    def __iter__(self):
        return iter(self.matching)

    def __bool__(self):
        return bool(self.matching)


class Signature:
    """A signature is a list that repersents the signature of a sentence.

    It is 'immutable' in that set operations are made inconvenent. And some
    simple type checks are performed. Other than that it is a convence
    wrapper."""

    def __init__(self, init):
        self._tokens = list(init)
        for token in self._tokens:
            if not isinstance(token, (Token, SubSentence)):
                raise TypeError('Invalid Signature value')

    def __len__(self):
        return len(self._tokens)

    def __iter__(self):
        return iter(self._tokens)

    def __getitem__(self, index):
        return self._tokens[index]

    def conflicts(self, other):
        """Check to see if Signatures conflict.

        Conflicting Signatures are not allowed to be defined in the same
        scope."""
        for i in range(min(len(self._tokens), len(other._tokens))):
            if (isinstance(self._tokens[i], Token) and
                    isinstance(other._tokens[i], Token) and
                    self._tokens[i] == other._tokens[i]):
                continue
            if (isinstance(self._tokens[i], SubSentence) and
                    isinstance(other._tokens[i], SubSentence) and
                    self._tokens[i] is not other._tokens[i]):
                return True
            return False
        else:
            return len(self._tokens) == len(other._tokens)

    def matches(self, sentence):
        """Check to see if the signature matches a list of tokens.

        A list (repersenting a Sentence) matches if all the words match,
        subsentences are in the same places."""
        self_len = len(self._tokens)
        sent_len = len(sentence)
        if not (self_len == sent_len or (self_len == sent_len - 1 and
                                         isinstance(sentence[-1], Token) and
                                         sentence[-1].kind == 'period')):
            return False
        for (my_token, other_token) in zip(self._tokens, sentence):
            pass
            # Check for equality.


# Idea: Why not take advantage of Multiple inheratance?
class SignatureElement:
    """A simple interface for elements that can be used inside a signature.

    Implementing classes must define equality."""

    def sig_match(self, other):
        if not isinstance(other, SignatureElement):
            raise TypeError()
        return (type(self) == type(other) and self == other)
