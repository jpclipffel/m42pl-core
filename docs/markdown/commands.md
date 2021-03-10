---
title: Commands
parent: M42PL
layout: default
nav_order: 2
---

# Commands

M42PL commands implements nearly all the project functionnalities, from the
language parsing to data processing.

## General syntax

A command call always start with a pipe symbol `|` followed by the command 
name and optionally by its arguments:

```
| command_name
| another_command arg1 arg2=value
| third_command [ | sub_command_1 ]
```

## Arguments syntax

Commands arguments respects the [fields syntax][fields]. Some arguments are
**static** while other are **dynamic**:

| Argument type | Documentation syntax | Description                                  |
|---------------|----------------------|----------------------------------------------|
| Static        | `<argument name>`    | Field is evaluated once when pipeline starts |
| Dynamic       | `{argument name}`    | Field is evaluated for each event            |

## Commands types

M42PL implements numerous commands of different types (generating, streaming, 
buffering and meta). Each command type specializes in a specific way to
manipulate events and pipeline.

### Generating commands

Generating commands generates (yields) events, usually from an external data
source (e.g. queues, HTTP requests, files, ...).

Notes:

* Generating commands yields events one by one
* A pipeline's or sub-pipeline's generating command may be preceded only by 
  one or more meta commands
* Only one generating command per pipeline or sub-pipeline may be defined
  * One may use sub-pipelines to chain generating commands

### Streaming commands

Streaming commands processes (manipulates) events one by one. Each received
event is processed then passed to the next command in the pipeline.

Notes:

* A streaming command may returns more or less than 1 event:
  * If the command filters events (e.g. the `where` command), some events may
    be discarded.
  * If the command generate new events from the recivev one (e.g. the
    `expand` command), new events will be returned instead of the original one

### Buffering commands

Buffering commands stores a given amount of events and then process them
all at once. Each processed event is then passed to the next command in the
pipeline.

Notes:

* Buffering commands may store only the latest version of an event (e.g. the
  `output` command)

### Meta commands

Meta commands can be placed anywhere in the pipeline and sub-pipelines.
They behave like streaming commands except they are designed to manipulate
the pipeline and sub-pipelines instead of events.


---

[fields]: ../fields/index.md