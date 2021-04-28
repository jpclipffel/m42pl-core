---
title: Fields
parent: M42PL
layout: default
nav_order: 3
has_children: true
---

# Fields

Fields are the way M42PL read and write **events attributes**.

In M42PL, each **event** is a comparable to a **JSON document**: they are
keys / values structures which contains keys of various types:

* String: A single value enclosed in double quotes: `"key": "a string"`
* Number: A number with or without a floating part: `"key": 42`, `"key": 42.21`
* Array: A sequence of sub-keys enclosed in square brackets: `"key": ["text data", 42, 42.21, {"key": "value"}]`
* Map: A structure of sub-keys encolsed in brackets: `"key": { "name": "some data" }`
* Binary: A binary data block

M42PL provides multiple **fields syntax** and **fields solvers** to access 
(read or write) fields:

## Numbers

Field solver: [LiteralField]

```
| make count=10
| eval value = 42
| output
```

## Strings

Field solver: [LiteralField]

```
| mpl_commands 'make'
```

## Variables

Field solver: [DictField]

```
| mpl_commands
| fields command.aliases, command.about
```

## Eval expressions

Field solver: [EvalField]

```
| make count=10 showinfo=yes
| foreach [
    | readfile path=`joinpath('path', 'to', 'files', id)`
]
```

## JSON path

Field solver: [JsonField]

```
| mpl_commands
| fields {command.aliases[0]}
```

## Sub-pipeline

Field solver: [PipeField]

```
| mpl_commands [ | make | eval command_name = 'jinja' ]
```

## Sequence

Field solver: [SeqnField]

```
TODO
```

---

[LiteralField]: ./literal.md
[EvalField]: ./eval.md
[DictField]: ./dict.md
[JsonField]: ./json.md
[PipeField]: ./pipe.md
