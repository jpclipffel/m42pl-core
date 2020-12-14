# M42PL

A data processing language (*in early alpha*).

## What is M42PL ?

M42PL is a *data processing language*, inspired by Bash, Python and
Splunk's SPL. The language scripts are *pipelines*, which generates and process
events in a streaming fashion.

Example:

```
| curl 'https://api.ipify.org' count=1
| fields response.content, response.status
| eval message = 'Your external IP is ' + response.content
| output format=json
```

You may find more examples in [the examples directory](/examples).

## Language semantics

M42PL grammar is extremely simple and easily extensible.

* The base unit is called a *script*
* A script is a list of commands separated by pipes `|`
* Each command consumes, processes and yields *events*
* Most command takes arguments:
  * Named arguments: `| commmand foo=42, bar='some text'`
  * Positional arguments: `| commmand 42, 'some text'`
* Arguments are dynamic and lazy-evaluated:
  * Literals (aka. constants): `| command foo='a string', bar=42`
  * Variables: `| command foo=myVarName`
  * Path variables: `| command foo=my.nested.var.name`
  * JSON-path variables: `| command foo={some.nested[1].variable}`
  * Sub-pipelines variables: `| command foo=[ | nested_command | other_command 'arg' ]`
* Commands may implements they own, custom grammar:
  * Example with `stats` command: `| stats count(field1) by field2`
  * Example with `eval` command: `| eval field_name = 'hello, ' + your.name`

## Components

M42PL is build on three components:

| Component           | Description                                | Link                                                      |
|---------------------|--------------------------------------------|-----------------------------------------------------------|
| `m42pl_core`        | Languages core (base classes, utils, etc.) | [GitHub](https://github.com/jpclipffel/m42pl-core)        |
| `m42pl_commands`    | Core commands                              | [GitHub](https://github.com/jpclipffel/m42pl-commands)    |
| `m42pl_dispatchers` | Core dispatchers                           | [GitHub](https://github.com/jpclipffel/m42pl-dispatchers) |

## Installation

* Create and activate a virtual environement:
  * `python3 -m virtualenv m42pl`
  * `source m42pl/bin/activate`
* Install the core language `m42pl_core`:
  * `git clone https://github.com/jpclipffel/m42pl_core`
  * `python3 -m pip install -e m42pl_core`
* Install the core commands `m42pl_commands`:
  * `git clone https://github.com/jpclipffel/m42pl_commands`
  * `python3 -m pip install -e m42pl_commands`
* Install the core dispatchers `m42pl_dispatchers`:
  * `git clone https://github.com/jpclipffel/m42pl_dispatchers`
  * `python3 -m pip install -e m42pl_dispatchers`
