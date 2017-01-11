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
FILERS.

## Overview ##
The steps of compilation and where the various source files come in:

*tokenize*: Turns raw text into a stream of tokens. This is context insenitive
and is run as input to the rest of Scribbler for all code input.

*parse*: Does a lot of heavy lifting, turns tokens into nested sentences. This
is context sensitive. To make the language cleaner the set of avalible
definitions is used to make decisions in parsing.

*tree* and *code* are competing a bit. The tree file has the parse tree
nodes and code has syntax tree nodes. Honestly they should probably be fused
together, but while I am working out the logic they are seperate.


Problem:
My biggest problem right now is how to handle subsentences and the two
different parse modes. (The parse modes cut off a bunch of other issues.)

The original plan was that it would be part of the signature:
`Define <signature> to be <expression>.`
This is the safe option, it is a bit harder to code but it is more powerful.
It can generate conflicts because the kind of subsentence has to be known
when we get to it.

The conventions to fix that problem lead to the idea that it is the tokens
that decide. Some tokens, such as `Define` act as flags saying that the
next sentence is a signature. This is simpler at this point (although it
pushes complexity to the Token) but is also harder to expand, and if it is
expanded more reserved flags have to be added.
