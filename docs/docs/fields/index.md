<!-- vim: set ft=Markdown ts=4 -->

# Fields

Fields are both the events _attributes_ and a way to access the given _attributes_.

M42PL's commands support 5 type of fields:

* [_Literal_](./literal.md): A literal value such as a number, a string or a list of values, e.g. `42`, `'some text'`, `(1, 2, 3)`
* [_Path_](./path.md): A field name or a doted field name, e.g. `field`, `field.subfield`
* [_Eval_](./eval.md): An evaulation expression, e.g. ```at(list, 0)```
* [_JsonPath_](./jsonpath.md): A _JsonPath_ expression, e.g. `{list[0].name}`
* [_Pipe_](./pipe.md): A sub-pipeline, e.g. `[ | kvread 'someName' ]`

## Fields interpretation

It is important to note that fields **values** are **dynamic** while
fields _types_ are _static_.

M42PL decides which field functor has to be instanciated using the
field syntax.

For example, the field `{user.emails[0]}` is matched as a `JsonPath` field.

Each time an event is processed, the same `JsonPath` instance will be called
with the event as first parameter to extrat the first item (`[0]`) in the list
`emails` in the root field `user`.


!!! note "Literal fields"
    Although _literal fields_ always return the same value, they are also
    implemented as functors in M42PL.

---
