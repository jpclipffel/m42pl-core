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

| Field example         | Description         | Command example                       | Field solver   |
|-----------------------|---------------------|---------------------------------------|----------------|
| `name`                | Variable name       | ``` \| rename foo as bar ```          | [LiteralField][] |
| `2`                   | Integer constant    | ``` \| make count=2 ```               | [LiteralField][] |
| `'json'`              | String constant     | ``` \| output format='json' ```       | [LiteralField][] |
| `` `True` ``          | Eval expression     | ``` \| make showinfo=`True` ```       | [EvalField][]    |
| `response.items`      | Field path variable | ``` \| fields response.items ```      | [DictField][]    |
| `{response.items[0]}` | JSON path variable  | ``` \| fields {response.items[0]} ``` | [JsonField][]    |
| `[\| read url.txt]`   | Sub-pipeline        | ``` \| wget url=[\| read url.txt] ``` | [PipeField][]    |

---

[LiteralField]: ./literal.md
[EvalField]: ./eval.md
[DictField]: ./dict.md
[JsonField]: ./json.md
[PipeField]: ./pipe.md
