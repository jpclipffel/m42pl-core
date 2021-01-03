---
layout: default
title: Eval field
nav_order: 1
parent: Fields
---

# Eval field

This field solver evaluates a Python expression and returns its results.

The evaluated expression has access to the current event fields and support the
same functions and syntax as the `| eval` and `| where` commands.

## Syntax

```
`<eval expression>`
```

Examples:

```
| make showinfo=`True`
| ...
```

```
| until `some.variable == 0` [
    ...
]
```
