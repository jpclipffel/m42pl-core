<!-- vim: set ft=Markdown ts=4 -->

# Evaluation functions

M42PL provides a custom _evaluator_ module which evaluates Python expression,
provides a set of utilities functions and a custom field accessing syntax.

## Misc functions

### field

Return the value of `<field_name>`, or `default_value` if not found.

```
field(<field_name>, [default_value])
```

### isnull

Returns true if `expression` is `None` or `null`, false otherwise.

```
isnull(<expression>)
```

### isnotnull

Returns true if `<expression>` is not `None` nor `null`, false otherwise.

```
isnotnull(<expression>)
```

### coalesce

Returns the first non-null expression. Return `None` if all `<expression>`
are `None` or `null`.

```
coalesce(<expression> [, ...])
```

### keys

Returns the keys of the given `field`, or all keys of no `field` is given.

```
keys([field])
```

---

## Time functions

### now

Returns the current time as an _epoch_ float.

```
now()
```

### reltime

Returns a relative time from the given [`<time expression>` (link)](./time.md)

```
reltime(<time expression>)
```

### strftime

Returns a string representation of `<expression>` using [`<format>` (link)](https://strftime.org/).

```
strftime(<expression>, [format]])
```

### strptime

Returns an _epoch_ float from the `<time string>` encoded with `<format>`.

```
strptime(<time string>, <format>)
```

---

## Cast functions

### tostring

Returns a string from the given `<expression>`.

```
tostring(<expression>)
```

### toint

Returns a string from the given `<expression>`.

```
toint(<expression>)
```

### tofloat

Returns a string from the given `<expression>`.

```
tofloat(<expression>)
```

## String functions

### clean

### split

### strip

---

## List functions

### list

### join

### slice

### idx

### length

---

## Math functions

### round

### even

### true

### false

---

## Filter functions

### match

---

## Path functions

### basename

### dirname

### joinpath

### cwd

---
