# Little Scribe: Language Definition #

This is my language definition of Little Scribe.

The syntax has been fairly set for a while now. However it will change as
I come up with new ideas, describe the idea better or have to make changes
for problems I did not forsee. Little Scribe is still in early development
and no aspect of it should be considered fixed at this point.

## Current ##

The language is comprised of a series of tokens that make up sentences. The
entire language is then built from nesting and listing sentences. Because of
this sentense make up (almost) every language feature.

##### Tokens:
+   Word: Made up of a string of characters. As Little Scribe is written, by
    default, in English the Latin alphabet is used. All characters are lower
    case
+   First Word: The first word in a sentence, as a regular word except the
    first letter is a capital, not lowercase.
+   Period: The token that ends a sentence.
+   Number: A token made up of digits, repersenting an integer value.

##### Levels:
Most sentences can occur anywhere, but not all, so we have a few levels where
sentences may or may not occur:
+   Page Level: File level, they are not a sentence within any other sentence.
+   Paragraph Level: At the same level as scope.
+   Sentence Level: An sentence nested within another sentence as an
    expression.

Currently the only difference is that page/paragraph level (they are equivant)
can have definitions while sentence level may not.

##### Values:
Currently values are treated specially and are always their own sentense.
Making them the only tokens with any inherit meaning.

##### Parsing Modes:
Not all parts of the file are read in the same way, but they are actually
so few we don't have to break them down by expressions, instead we have parse
modes:
+   Normal: Sentences matching existing definitions are read in, a period
    can close any number of sentences, but will close the fewest possible.
+   Signature: Reads in a signature for a new definition, it does not have to
    (indeed, should not) match any existing definition. A period always ends
    1 sentence.

##### REPL (Read-Evaluate-Print-Loop):
Currently the program acts through a REPL interface. Each sentence at the page
level is read, evaluated and usually printed, definitions are not printed and
are instead added to the scope.

##### Functions:
Generally a sentence can be considered a function. They can act as variables
and parameters, but for now those are special 0 argument functions.

After a sentence is read in it is matched with a function of the same form.
All the words (including the first word) must match a definition. This is also
true of the location (but not the content) of the subsentences of that
sentence.

All subsentences are evaluated first and then passed in as parameters. Within
the function body, the subsentences from the signature are functions that
return the value of that parameter.

The only exception is the function definition sentence itself, which does not
evaluate its subsentences.

## Future ##

These planned features are here just to help me keep them in mind.

Of course the built in functions will have to be expained, we need a lot of
base operations and so on. `Add Left hand side. to Right hand side. .`
`If Condition. then Then block. else Else block. .`

Add operators, which should work similarly to normal sentences.
`Define operator ( Any. ) to be Any.`

Add type/struture definitions:
`Define structure Pair. to be Left. Right.`
The syntax for that is not set, and I have to ideas for field access:
`Get Field. from Instance.` and `Instance Field.` The later is cleaner but may
be ambiguous, and isn't as clear.

Add type checking on functions:
`Define Operation Input. . as a Function Input type. returning Output type.`
I hope to keep that some what seperate as adding type notations does not flow
in this language, but at the same time the type checks are just useful to
ensure correctness, so I would like to add them.

Add more built in types such as strings `"String"`, characters `'c'` and
floating point numbers `3.14`.

Add imports and support for moduals: `Import "file/path.name".`

Add nested scopes, at first this will probably always have to be done
explicately with `Begin ... end.` but later may become a implied feature
in some locations. It might be a new type of SubSentence: `SubBlock`

Add support for lists of arguments. I'm thinking of using the comma for that.

Add support for functions as arguments. The second level of parameters
(the ones not supposed to be filled in at call time) is the only thing that
should need any new syntax.
