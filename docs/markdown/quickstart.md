---
title: Quick start
parent: M42PL
layout: default
nav_order: 1
---

# Requirements

* Python >= 3.9

# Installation

Create and activate a virtual environement:

```shell
python3 -m virtualenv m42pl
source m42pl/bin/activate
```

Install the core language `m42pl-core`:

```
git clone https://github.com/jpclipffel/m42pl-core
pip install m42pl-core
```

Install the core commands `m42pl-commands`:

```
git clone https://github.com/jpclipffel/m42pl-commands
pip install m42pl-commands
```

Install the core dispatchers `m42pl-dispatchers`:

```
git clone https://github.com/jpclipffel/m42pl-dispatchers
pip install m42pl-dispatchers
```

# Usage

M42PL can executes scripts or can be run as an interpreter. M42PL scripts are
standard text files.

To start an interpreter, run the command `m42pl repl` (type `exit` to leave):

```
$ m42pl repl
m42pl |
```

You may run a M42PL script using the `m42pl run` command:

```
$ m42pl run <filename.mpl>
```

A M42PL script is a **pipeline** (a list of **commands** starting with
pipes `|`):

```
| make | eval hello = 'world !' | output
```

* `make` generates events
* `eval` evaluates Python expressions and assign results to fields
* `output` print events on the standard output

You can separate commands with new lines too (new lines are ignored):

```
| make
| eval hello = 'world !'
| output
```

The list of available commands and their associated documentation can be
obtained by running the command `mpl_command`:

```
| mpl_command
```

To get information about a specific command, run `mpl_command` followed by the
command name:

```
| mpl_command 'make'
```

Most commands takes **parameters** (aka. **fields**):

```
| make 2 showinfo=yes
| output
```

* **positional parameters** have no name (ex: `2`)
* **named parameters** are prefixed with their name (e.g. `showinfo=yes`)

Commands **fields** (aka. **parameters**) have various types:

| Snippet                        | Field                 | Description         |
|--------------------------------|-----------------------|---------------------|
| `| make count=2`               | `2`                   | Integer constant    |
| `| output format='json'`       | `'json'`              | String constant     |
| `| fields response.items`      | `response.items`      | Field path variable |
| `| fields {response.items[0]}` | `{response.items[0]}` | JSON path variable  |
| `| wget url=[| read url.txt]`  | `[| read url.txt]`    | Sub pipeline        |

A comment is a call to the `| ignore` or `| comment` command:

```
| make
| ignore eval foo='bar'
| output format=json
```

Commands have multiple names; the following snippets are identical:

```
| make | eval foo='bar' | output
```

```
| makeevent | evaluate foo='bar' | print
```

Three types of commands exists:

* **Generating**: One per pipeline; Generate events (e.g. performs an HTTP
  request, read a file, consume a queue, etc.)
* **Streaming**: Process events as they arrive. As many as needed per pipeline.
* **Meta**: Control the pipeline behaviour and parameters. As many as needed
  per pipeline.

Having a single generating command per pipeline may looks limitating; But M42PL
supports **sub-pipelines**:

```
| read 'list_of_urls.txt'
| foreach [
    | wget url
    | fields response.content
]
| output
```

Commands may also implements their own, custom grammar:

```
| make count=2 showinfo=yes
| rename id as 'event.id'
```

You can create and uses macros (reusable pipelines) with the `| macro` command:

```
| macro 'output' [ | output format=json ]

| make showinfo=yes
| macro output
```
