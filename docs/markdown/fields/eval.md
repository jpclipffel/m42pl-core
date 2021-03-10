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

Read a file content using `readfile` with a `path` argument built using the
`joinpath` function:

```
| readfile path=`joinpath('/some/path', filename)`
```

(re)Run a sub-pipeline until the expression becomes true (`some.variable` is `0`):

```
| until `some.variable == 0` [
    ...
]
```
