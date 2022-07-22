# Reusability

## Macros

M42PL supports _macros_, which are reusable pipelines stored in a _KVStore_.

The list of available macros can be found be using the `macros` command:

```
| macros
```

A macro can be defined or updated by running the `macro` command followed
by its pipeline definition. In the next example, we define the macro `make_n`
which generates the requested number of events, or `1` by default:

```
| macro make_n [ | make count=`field(count, 1)` ]
```

You can invoke a macro with the same `macro` command, optionally followed
by a list of macros parameters:

```
| macro make_n
```

```
| macro make_n count=2
```

Macros can be called as first command, or as an intermediate command in your
pipeline.

---
