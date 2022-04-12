# First Steps

## Start the command line

Once M42PL is installed ([installation instructions][install]), you may run it
in REPL (interactive) mode:

If installed locally:

```shell
m42pl repl
```

If installed locally in a virtual environement:

```shell
source m42pl/bin/activate
m42pl repl
```

If installed using Docker:

```shell
docker run -it jpclipffel/m42pl repl
```

## Command line usage

> **Hint**  
> The M42PL REPL runs in multi-lines edit, which means than pressing
> `Enter` will literally add a new line. To execute the commands you
> typed, press `Esc` then `Enter`.

The M42PL language is extremelly simple:

* A program / script is a list of _commands_
* A command starts with the pipe `|` character
* A command may takes _argument(s)_ (also known as _fields_)

This is an _Hello World_ example:

```
| eval hello='world'
```

At any point, you may run a _builtin_:

* `help`: Display a quick REPL help
* `exit`: Quit the REPL

You can get a list of available commands by running the `commands` command:

```
| commands
```

Lets keep only the fields we're interested in, namely `command.alias`
and `command.about`:

```
| commands
| fields command.alias, command.about
```

You may notice that some duplicates `command.about` appears; this is because
many commands have _aliases_, i.e. multiple names.

To regroup the command which have the same description, you may use `stats`:

```
| commands
| fields command.alias, command.about
| stats values(command.alias) as aliases by command.about
```

Finally, to generate a nice single-line description of each command, it aliases
and its description:

```
| commands
| fields command.alias, command.about
| stats values(command.alias) as aliases by command.about
| eval man = join(aliases, ', ') + ': ' + command.about
| fields man
```

## Commands types



---

[install]: installation.md
