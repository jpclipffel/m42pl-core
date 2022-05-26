# REPL

Runs M42PL as a REPL (interactive command interpreter).

```shell
m42pl repl
```

## General usage

* M42PL' REPL read multiples lines at once; to execute the pipeline you typed,
  hit `Escape` then `Enter`
* When a pipeline is running, type `Ctrl+c` to stop it
* You can use the arrow keys to move in history and in the pipeline source
* The REPL automatically adds an `output` command to your pipeline if you didn't
  added a similar command; use another dispatcher (`-d <dipatcher name>`) such
  as `local` to avoid this behaviour

## Arguments

> **Tip**  
> Run `m42pl repl -h` or `m42pl repl --help` to get help

> **TODO**  
> Document REPL arguments

## Builtins commands

The REPL provides some builtins commands:

| Builtin         | Description                               |
|-----------------|-------------------------------------------|
| `exit`          | Exists the REPL                           |
| `modules`       | Prints the list of loaded modules         |
| `import <name>` | Imports the module `<name>`               |
| `reload`        | Reloads the imported modules              |
| `help`          | Prints help                               |
| `cd <path>`     | Changes the working directory to `<path>` |
| `pwd`           | Prints the current working directory      |
| `ml [on|off]`   | Multi-line edit switch                    |
| `plan [on|off]` | Plan mode switch                          |

## Prompt customization

You can change the prompt prefix using `-p` or `--prefix` to provide an HTML
string. Some standard _PS1_ builtins are supported as well.

> **Tip**  
> Do not forget to close the HTML tags, e.g. `<bold>...</bold>`

| Syntax         | Kind        | Description                               |
|----------------|-------------|-------------------------------------------|
| `{w}`          | PS1 builtin | Replaced by the current working directory |
| `{u}`          | PS1 builtin | Replaced by the current user name         |
| `<bold>`       | HTML tag    | Write text in **bold**                    |
| `<color name>` | HTML tag    | Write text in the given _color name_      |

---
