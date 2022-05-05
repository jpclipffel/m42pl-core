<!-- vim: set ft=Markdown ts=4 -->

# Evaluated fields

Evaluated fields returns the result of an [evaluation expression]().
They are similar to some programming languages _lambdas_.

## Syntax

Evaluated fields are enclosed in back-quotes:

```
current_year=`strftime(now(), '%Y')`
```

## Example

Write the output of the command `ps aux` in files, with on file per user name.

Script:

```
| process 'ps' 'aux'
| regex line with '(?P<user>[^\s]+).*'
| writefile `line + '\n'` to `'/tmp/processes-' + user + '.log'`
```

Generated files (truncated output):

```shell
ls -l /tmp/processes-*

-rw-rw-r-- 1 ... /tmp/processes-avahi.log
-rw-rw-r-- 1 ... /tmp/processes-colord.log
-rw-rw-r-- 1 ... /tmp/processes-message+.log
-rw-rw-r-- 1 ... /tmp/processes-root.log
-rw-rw-r-- 1 ... /tmp/processes-syslog.log
-rw-rw-r-- 1 ... /tmp/processes-systemd+.log
-rw-rw-r-- 1 ... /tmp/processes-USER.log
-rw-rw-r-- 1 ... /tmp/processes-uuidd.log
```
