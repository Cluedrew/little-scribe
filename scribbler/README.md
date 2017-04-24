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


New Plan:
Because I think I have figured out enough to create a new plan.

I am going to need keywords, I thought the use of built in functions would
replace that, but it will not completely. `Define` will have to be a keyword.
It will do the following:
+   The first sub-sentence in the sentence is read in signature parse mode.
+   That sub-sentence, and all of its direct sub-sentences will be avalible in
    the later sub-sentences.
+   None of the sub-sentences are evaluated before passing them to the
    function, it must take the raw sentences.

This should match conventions I that (planned) before, but lets the parser
know these things. Define sentences will almost always create a new
definition, the first sub-sentence (however this is not enforced), the other
rules allow this by given access to the text and allowing for self referental
and parameterised definitions.

Definitions use the full signature, parameters will be repersented by sub-
sentences instead of markers. This means the sentence can directly used as
the signature and they can have the names stored in line. Types might have
to be stored in parallel, but I think that is fine. The parsing information
has of course been move to the Define keyword.

Function definitions will keep a copy of the scope they are defined within.
It can be updated but it should retain all of the definitions the function
needs. It can then create an internal scope with all the parameters. I am
not sure how this will handle nested functions, but we don't have that yet.

I may use an 'Action' type to implement definitions, which are just values
of a type that the environment executes instead of printing. They have access
to the enclosing scope for this, so they can add definitions.

I am dropping binding of definitions to sentences, I've taken out some of it
all ready. The binding would be great for efficiency but requires some over
head that is just not need now. We will look up a sentence when we need it.

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
