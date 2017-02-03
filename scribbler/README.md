# Scribbler #

Scribbler is the default compiler for Little Scribe.

## Usage ##
scribbler [OPTIONS] [--] (FILES...)

scribbler will run, reading definitions from each file in turn. It will then
enter interactive mode with a REPL (Read Evaluate Print Loop) until the end of
input.

### OPTIONS
None of these are supported yet.

##### -x --exit
Do not enter interactive mode. Exit imediately on finishing reading in all
FILES.

##### -i --ignore-errors[=N]
If there is an error reading a paragraph, continue trying to read in later
paragraphs rather than quit immediately. If 

## Overview ##
Sections of code and their source files:

*tokenization* (*tokenize*):
Conversion of text to tokens. This is a pretty solid line between the outside
world and the rest of Scribbler, even the raw text Scribbler deals with is
burried in a token first. Tokenization is context-free and is uneffected by
other changes in the program.

*parse tree* (*parse*, *tree*, *signature*):
Conversion of tokens into a parse tree. The types of parse tree nodes are as
follows.
+ **ParseTreeNode** - Abstract Base Class. It isn't used for anything except
    giving all the nodes in the parse tree some standard features.
+ **Sentence** - An executable statement, these include definitions
    (interprated language), varables and function calls.
+ **Pattern** - Context-free branch node that defines a function signature.
    They cannot be used as expressions, cannot be evaluated, do not return
    a value.
+ **Token** - Tokens are the leaf nodes in this tree. Generally they have no
    meaning until grouped into a sentence. (Defined in *tokenize*.)

(Make Sentence a parent to Pattern and have Expression be the general sentence
type?)

There are also two parse nodes:
+ **signature**, or pattern mode: Used to read in pattern and create new
    signatures. While in signature mode every FirstWord begins a sentence and
    every Period ends a sentence.
+ **normal** mode: Used the rest of the time, when we are reading in Sentences
    to create expressions. The important difference is that periods can end
    multiple sentences, and the types of nested sentences can vary. This
    requires knowledge of the avalible Patterns and so is context-sensitive.

Period Rules: In signature mode a period always ends the current pattern. In
normal mode a period will try to end the current sentence (try here means
check to see if what has been read in so far matches a Pattern in scope) and
will raise an error if it cannot. It will then try to continue the last
Sentence by reading in the next token. If there is no Pattern that matches it
will try to end that Sentence as well. If it cannot it raises an error. If it
can it reapeats that with the next higher Sentence.

Why all that complexity? (Seriously, drop that one feature, parsing becomes
context-free.) Because of the LISP problem, where functions will end with
blocks like `)))]))]))` because the deep nesting suddenly ends. With this
rule `.........` becomes `.`. Also I have found it to actually be pretty
intuitive in my test writes.

*scoping* (*scope*):
A Scope is a collection of the current definitions, currently immutable once
set. The top level scope starts with all the built in definitions in it.
Definitions can be added, but they will be rejected if they conflict with any
existing definitions.

Definisions have two (three) parts.
1. A pattern that defines when it is used.
2. A body that is used to resolve the execution. Returns some value.
3. A type (maybe) which allows for some basic type checking.


Problems:
My biggest problem right now is how to handle subsentences and the two
different parse modes. (The parse modes cut off a bunch of other issues.)
Does it go by signature: `Define <signature> to be <expression>.` Or by Token,
so that `Define` means the next subsentence is a signature.

The way the files are laid out should probably change. I was originally going
for a more stuctures & functions approach but that doesn't work with Python
as well. So I might convert it over which means files will be originized by
class instead of step in the logic.
