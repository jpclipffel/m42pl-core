# M42PL

M42PL is a *data processing language*, inspired by Bash and Splunk's SPL.

The language is designed to be as easy as possible to use, and to make common 
scripting and programming tasks even easier. It does not have a tedious syntax
to learn, and hides advanced programming concepts from the user.

Nearly all language features are implemented in **commands** which are
dynamically loaded from one or more **plugins** directory(ies).

Example:

```shell
| url 'https://api.ipify.org'
| fields response.content, response.status
| eval message = 'Your external IP is ' + response.content
| output format=json
```

You may find more examples in [the examples directory](/examples).

The core commands [are available here][m42pl-commands]. Some example:

* `| url`: Performs HTTP requests
* `| eval`: Evaluate fields using Python expressions
* `| xpath`: Extract fields using an XPath expression

## Quick introduction

M42PL can executes scripts or can be run in REPL mode. M42PL scripts are
standard text files, which may end with `.mpl` or `.m42pl`.

To start an interpreter, run the command `m42pl repl` (type `exit` to leave):

```
$ m42pl repl
m42pl |
```

Mandatory *hello world* script:

```shell
| make | eval hello = 'world !'
```

You may run a M42PL script using the `m42pl run` command:

```shell
$ m42pl run <filename.mpl>
```

A M42PL script is a **pipeline** (a list of **commands** starting with
pipes `|`):

```
| make | eval foo='bar' | output
```

You can separate commands with new lines too (new lines are ignored):

```
| make
| eval foo='bar'
| output
```

Most commands takes **parameters** (aka. **fields**):

```
| make 2 showinfo=yes
| output
```

* **positional parameters** have no name (ex: `2`)
* **named parameters** are prefixed with their name (e.g. `showinfo=yes`)

Commands **fields** (aka. **parameters**) support various syntax:

| Example                        | Field                 | Description         |
|--------------------------------|-----------------------|---------------------|
| `| make count=2`               | `2`                   | Integer constant    |
| `| output format='json'`       | `'json'`              | String constant     |
| ``` | make showinfo=`True` ``` | `` `True` ``          | Eval expression     |
| `| fields response.items`      | `response.items`      | Field path variable |
| `| fields {response.items[0]}` | `{response.items[0]}` | JSON path variable  |
| `| wget url=[| read url.txt]`  | `[| read url.txt]`    | Sub-pipeline        |

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

## Components

M42PL is build on three components:

| Component           | Description                                | Link                                                      |
|---------------------|--------------------------------------------|-----------------------------------------------------------|
| `m42pl_core`        | Languages core (base classes, utils, etc.) | [GitHub](https://github.com/jpclipffel/m42pl-core)        |
| `m42pl_commands`    | Core commands                              | [GitHub](https://github.com/jpclipffel/m42pl-commands)    |
| `m42pl_dispatchers` | Core dispatchers                           | [GitHub](https://github.com/jpclipffel/m42pl-dispatchers) |

### Core

Implements the base classes and the language utilities.

* [Documentation](/docs/markdown)
* [Technical documentation](/docs/sphinx)

### Commands

Implements most of M42PL functionnalities.

* [Repository link][m42pl-commands]

### Dispatchers

Implements M42PL execution method (local, multi-processing, Celery, etc.).

* [Repository link][m42pl-dispatchers]

## Installation

Create and activate a virtual environement:

```shell
python3 -m virtualenv m42pl
source m42pl/bin/activate
```

Install the core language `m42pl_core`:
```
git clone https://github.com/jpclipffel/m42pl-core
pip install m42pl-core
```

Install the core commands `m42pl_commands`:
```
git clone https://github.com/jpclipffel/m42pl-commands
pip install m42pl-commands
```

Install the core dispatchers `m42pl_dispatchers`:
```
git clone https://github.com/jpclipffel/m42pl-dispatchers
pip install m42pl-dispatchers
```

## FAQ

### Is M42PL a programming language ?

No; I like to call it a *data processing language* because it is not designed
to be a competitor to programming languages such as Python, Haskell, C++, etc.

### Is this useful in any way ?

Maybe it can be useful for people who program data flows (e.g. for
prototyping), or for people who do not program and just want a quick and easy
way to collect and process data.

### Where does this thing come from ?

I used to work with Splunk and Elastic Search a lot in a previous job.
I loved both products, but I always had the feeling that Elastic Search's DSL
syntax was too tedious and Splunk's SPL was too limitating.

I initially wanted to write a tool to query Elastic Search with the same
language as Splunk, but I quickly drifted from my goal.

---

[m42pl-commands]: https://github.com/jpclipffel/m42pl-commands
[m42pl-dispatchers]: https://github.com/jpclipffel/m42pl-dispatchers
