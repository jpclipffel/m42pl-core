---
title: Eval field
parent: Fields
layout: default
---

# Eval field

This field solver evaluates a Python expression and returns its results.

The evaluated expression has access to the current event fields and support the
same functions and syntax as the `eval` and `where` commands.

## Syntax

* Positional argument: ``` | command `<expression>` ```
* Named argument: ``` | command <field>=`<expression>` ```

## Examples

Read a file line by line using `readlines` with a `path` argument built with
the `joinpath` function:

```
| readlines path=`joinpath(root, filename)`
| ...
```

Run a sub-pipeline until a becomes true (`some.variable` must be `42`):

```
| until `some.variable == 42` [
    | ...
]
```
