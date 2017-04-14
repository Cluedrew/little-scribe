# Scribbler #

Scribbler is the default compiler for Little Scribe.

Currently it is very much in the "minimum viable product" stage. Very few
features are implemented and I will probably have to redo a lot of the code
once I have a better idea of how to design this progam.

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

*parse tree* (???):
Conversion of tokens into a parse tree. Tokens are the leaf nodes and
Sentences are the internal branch nodes. How Sentences are constructed depends
on the parse mode (normal or signature, see below).

*scoping* (*scope*):
A Scope is a collection of the current definitions, currently immutable once
set. The top level scope starts with all the built in definitions in it.
Definitions can be added, but they will be rejected if they conflict with any
existing definitions.

Definisions have two (three) parts.
1. A pattern that defines when it is used.
2. A body that is used to resolve the execution. Returns some value.
3. A type (maybe) which allows for some basic type checking.

While we are parsing we check against a DefinitionGroup, which is a collection
off all the Definition the current Sentence could match. (Ignored in signature
parse mode.)

*built ins* (*built_in*):
Built in functions are manually created and loaded into the top-level scope
when we begin executing.


Problems:
My biggest problem right now is how to handle subsentences and the two
different parse modes. (The parse modes cut off a bunch of other issues.)
Does it go by signature: `Define <signature> to be <expression>.` Or by Token,
so that `Define` means the next subsentence is a signature.

New related problem, the <signature> (the main Sentence and its children)
have to be availible in <expression> so that they can be matched. Which means
we have to stop after the signature

The way the files are laid out should probably change. I was originally going
for a more stuctures & functions approach but that doesn't work with Python
as well. So I might convert it over which means files will be originized by
class instead of step in the logic.

Execution
I realized I am fooling myself by trying to create parsing and execution
seperately. Well they are sort of seperate, but they are tied together in the
REPL.

On each Page (for now, we will have one page/source file) we read in a
paragraph and evaluate a result. The result can be an Action object which is
then executed (usually modifying the scope), if it is not we convert the
object to a string and print it.

So I have the basic page-paragraph-sentence/signature layout in the parser
already. Might need some work. Main issue is I need a way to check an existing
sentence against a signature. Both for normal parse mode and actually checking
function definitions at the end.

##### Parsing Patterns
There are two parse modes:
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
