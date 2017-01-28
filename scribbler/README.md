# Scribbler #

Scribbler is the default compiler for Little Scribe.

## Usage ##
scribbler [OPTIONS] [--] (FILES...)

scribbler will run, reading definitions from each file in turn. It will then
enter interactive mode with a REPL (Read Evaluate Print Loop) until the end of
input.

### OPTIONS
##### -x --exit
Do not enter interactive mode. Exit imediately on finishing reading in all
FILES.

## Overview ##
The steps of compilation and where the various source files come in:

*tokenize*: Turns raw text into a stream of tokens. This is context insenitive
and is run as input to the rest of Scribbler for all code input.

*parse*: Does a lot of heavy lifting, turns tokens into nested sentences. This
is context sensitive. To make the language cleaner the set of avalible
definitions is used to make decisions in parsing.

*tree*: Defines all/some of the base types used to repersent the parse tree.
I think I am going to have to work on it a bit more:
= ParseTreeNode - Abstract Base Class. It isn't used for anything except
      giving all the nodes in the parse tree some standard features.
== Sentence - This might be a paragraph because all Sentences can be used as
      Paragraphs, but not the other way around. This is the "standard"
      sentence used in most places. I sometimes will call it an expression
      to say it is NOT one of the other types.
=== Signature - Context-free sentence, used to define function signatures,
      which may have to be another type. These ones are actually parsed
      differently than the others (currently the only one).
=== Paragraph - The top level Sentences that can modify a scope. They may
      have some special code to allow that or... Maybe it returns an operation
      that does the work?
=== PageSentence? - Do I need a type for page level?
== Token - Tokens are not Sentences, even in the case only one Token in the
      sentence. However they are the leaves of the parse tree.


Problems:
My biggest problem right now is how to handle subsentences and the two
different parse modes. (The parse modes cut off a bunch of other issues.)
Does it go by signature: `Define <signature> to be <expression>.` Or by Token,
so that `Define` means the next subsentence is a signature.

The way the files are laid out should probably change. I was originally going
for a more stuctures & functions approach but that doesn't work with Python
as well. So I might convert it over which means files will be originized by
class instead of step in the logic.
