# M42PL

M42PL is a **data processing language**, inspired by Unix shells and
[Splunk][splunk].

The language is designed for streams manipulation and provides a wide amount of
commands to collect and process data. It focuses on simplicity and hides
advanced programming concepts from the user.

Some code examples:

**Query an URL**

```
| url 'https://api.ipify.org'
| fields response.content, response.status
| eval message = 'Your external IP is ' + response.content
| output format=json
```

**Run a HTTP server**

```
| http_server with
    '*' on '/foo' = [
        | echo
        | eval path='foo', mode='infinite+iterator'
        | fields path, mode
    ],
    '*' on '/bar' = [
        | eval path='bar', mode='infinite+stream'
        | fields path, mode
    ],
    '*' on '/{path}' = []
```

**Capture and stream a video**

> This requires the installation of the [lab commands][m42pl-git-commands-lab]

```
| cv2_read
| cv2_resize ratio=0.5
| zmq_pub topic='webcam'
```

**Display a video stream**

> This requires the installation of the [lab commands][m42pl-git-commands-lab]

```
| zmq_sub topic='webcam'
| decode {zmq.frames[0]} with 'msgpack'
| cv2_show cv2.frame
```


You may find more examples in [the examples directory](/examples/README.md).

Nearly all language features are implemented in **commands** which are
dynamically loaded from **plugins**. The core commands
[are available here][m42pl-git-commands]. Some example:

* `url`: Performs one or more parallel HTTP requests
* `eval`: Evaluate fields using Python expressions
* `xpath`: Extract fields using an XPath expression
* `stats`: Performs statistical operations and aggregations

## M42PL specificities

* Commands may implements their own custom grammar (like the `stats` command),
  which means that only the `|` (pipe) and `[]` (sub-pipeline) structures are
  part of the core language
* M42PL runs *on* a Python interpreter, but its execution is managed by
  **dispatchers** which controls *how* and *where* the code is ran: on the
  local interpreter, on multiple processes, on Celery nodes, etc.
* Most fields (commands arguments) in M42PL behaves like lambdas; To refers to
  the field `user.name`, you can write:
  * `data=user.name` (direct access)
  * `data={user.name}` (in-line JsonPath expression)
  * ```data=`field(user.name)` ``` (in-line eval statement)
  * `data=[ | curl '...' | fields response.json.name ]` (in-line sub-pipeline)

## Quick introduction

M42PL can run scripts or can be run in REPL mode. M42PL scripts are
standard text files, which end with `.mpl` or `.m42pl` by convention.

To start an interpreter (REPL), run the command `m42pl repl`
(type `exit` to leave):

```
$ m42pl repl
m42pl |
```

Mandatory *hello world* script:

```
| make | eval hello = 'world !'
```

You may run a M42PL script using the `m42pl run` command:

```shell
$ m42pl run <filename.mpl>
```

A M42PL script is a **pipeline** (a list of **commands** starting with
pipes `|`):

```
| make | eval foo = 'bar' | output
```

You can separate commands with new lines too (new lines are ignored):

```
| make
| eval foo = 'bar'
| output
```

Most commands takes **parameters** (aka. **fields**):

```
| make 2 showinfo=yes
| output
```

* **positional parameters** have no name (ex: `2`)
* **named parameters** are prefixed with their name (ex: `showinfo=yes`)

Commands **parameters** (aka. **fields**) support various syntax:

| Example                               | Field                 | Description         |
|---------------------------------------|-----------------------|---------------------|
| ``` \| make count=2 ```               | `2`                   | Nunber              |
| ``` \| output format='json' ```       | `'json'`              | String              |
| ``` \| make showinfo=`True` ```       | `` `True` ``          | Eval expression     |
| ``` \| fields response.items ```      | `response.items`      | Field path variable |
| ``` \| fields {response.items[0]} ``` | `{response.items[0]}` | JSON path variable  |
| ``` \| wget url=[\| read url.txt] ``` | `[\| read url.txt]`   | Sub-pipeline        |

A comment is a call to the `| ignore` or `| comment` command:

```
| make
| ignore eval foo='bar'
| output format=json
```

Commands have **multiple names** (aka. **aliases**); The following snippets
are identical:

```
| make | eval foo='bar' | output
```

```
| makeevent | evaluate foo='bar' | print
```

Five types of commands exists:

* **Generating**: One per pipeline; Generate events (e.g. performs an HTTP
  request, read a file, consume a queue, etc.)
* **Streaming**: Process events as they arrive. As many as needed per pipeline.
* **Buffering**: Process events batches. As many as needed per pipeline.
* **Meta**: Control the pipeline behaviour and parameters. As many as needed
  per pipeline.
* **Merging**: Indicates that a split pipeline must be merged.

Having a single generating command per pipeline may looks limitating, but M42PL
supports **sub-pipelines**:

```
| readfile 'list_of_urls.txt'
| foreach [
    | wget url
    | fields response.content
]
```

Commands may also implements their own, custom grammar:

```
| make count=10 showinfo=yes
| rename id as event.id
| eval is_even = even(event.id)
| stats count by is_even
```

## Components

M42PL is build on four components:

| Component           | Description                                | Link                            |
|---------------------|--------------------------------------------|---------------------------------|
| `m42pl_core`        | Languages core (base classes, utils, etc.) | [GitHub][m42pl-git-core]        |
| `m42pl_commands`    | Core language commands                     | [GitHub][m42pl-git-commands]    |
| `m42pl_dispatchers` | Executes M42PL scripts and REPL            | [GitHub][m42pl-git-dispatchers] |
| `m42pl_kvstores`    | Key/values stores support                  | [GitHub][m42pl-git-kvstores] |
| `m42pl_encoders`    | Encode and decode data formats             | [GitHub][m42pl-git-encoders]    |

You may find extra components packages such as
[the lab commands][m42pl-git-commands-lab].

### Core

Implements the base classes and the language utilities.

* [Documentation](/docs/markdown)
* [Technical documentation](/docs/sphinx)

### Commands

Implements most of M42PL functionnalities.

* [Repository link][m42pl-git-commands]
* [Documentation][m42pl-docs-commands]

### Dispatchers

Implements M42PL execution method (local, multi-processing, Celery, etc.).

* [Repository link][m42pl-git-dispatchers]

### Key/value stores

Implements M42PL key/value stores.

* [Repository link][m42pl-git-kvstores]

### Encoders

Implements data format casting encoding and decoding (e.g. cast to
`msgpack`, `JSON`, `bson`, etc.).

* [Repository link][m42pl-git-encoders]

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

Install the core kvstores `m42pl_kvsotres`:
```
git clone https://github.com/jpclipffel/m42pl-kvstores
pip install m42pl-kvstores
```

Install the core encoders `m42pl_encoders`:
```
git clone https://github.com/jpclipffel/m42pl-encoders
pip install m42pl-encoders
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
language as Splunk, but I quickly drifted from my original goal.

---

[splunk]: https://splunk.com
[m42pl-git-core]: https://github.com/jpclipffel/m42pl-core
[m42pl-git-commands]: https://github.com/jpclipffel/m42pl-commands
[m42pl-git-commands-lab]: https://github.com/jpclipffel/m42pl-commands-lab
[m42pl-git-dispatchers]: https://github.com/jpclipffel/m42pl-dispatchers
[m42pl-git-kvstores]: https://github.com/jpclipffel/m42pl-kvstores
[m42pl-git-encoders]: https://github.com/jpclipffel/m42pl-encoders
[m42pl-docs-commands]: https://mine42.io/m42pl/m42pl-commands
