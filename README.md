# little-scribe #

I have often dreamed of creating a new programing language that would solve
all the issues I have with all the current programing languages. This is not
that language. This is kind of a joke.

I am going through with the joke as a learning exersise.

### Language Definition
The language definition is quite simple at this stage. It is functional and
dynamically typed.

The language is constructed from sentences. A sentence starts with a capital
letter, consists of white space seperated words and ends in a period.

`This is a valid sentence.`

Sentences combine what is covered by itentifiers, statements and expressions
in other languages. Sentences can also be nested.

`Add Length of wait. to Start time. .`

I am also hoping to add the ability for a period to end multiple sentences,
as the chains of dots look messy. This will not work in all cases but it
helps in some cases.

### Built-Ins
There are no built-ins yet (running a program has no effect) but here is
the first one I am aiming for:

`Define Function signature. to be Function definition. .`

### Scribbler
This is my compiler for Little Scribe. It is implemented in Python because it
is fast to write, widely used language that I know and that shares some
characteristics of Little Scribe.
