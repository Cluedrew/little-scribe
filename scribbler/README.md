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

Problems:
My biggest problem right now is how to handle subsentences and the two
different parse modes. (The parse modes cut off a bunch of other issues.)
Does it go by signature: `Define <signature> to be <expression>.` Or by Token,
so that `Define` means the next subsentence is a signature.

The way the files are laid out should probably change. I was originally going
for a more stuctures & functions approach but that doesn't work with Python
as well. So I might convert it over which means files will be originized by
class instead of step in the logic.
