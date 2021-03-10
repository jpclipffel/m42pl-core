---
title: Literal field
parent: Fields
layout: default
---

# Literal field

This field solver searches a field by its name and returns its value.
If the field points to a number or a string (enclosed in simple or double
quotes), the number or string value is returned.

## Syntax

* Variable: `some_field`
* String: `'signle-quoted string'`, `"string in double quotes"`
* Number: `42`, `42.21`

## Examples

```
| rename field_name as "new field name"
```
