<!-- vim: set ft=Markdown ts=4 -->

# Time expressions

M42PL provide a time expression syntax to select time ranges.

The general expression syntax is:

```
(-|+)<value><unit>@<precision>
```

Where:

* `(-|+)` indicates if you decrement (`-`) or increment (`+`) the time offset
    * By default, M42PL assumes you decrement (`-`)
* `<value>` is an integer, representing the number of `<unit>` to decrement or increment
* `<unit>` is the time unit in:
    * `ms`: microsecond
    * `s`: second
    * `m`: minute
    * `h`: hour
    * `d`: day
    * `mon`: month
* `<precision>` is the current time rounded to:
    * `now`: microsecond
    * `s`: second
    * `m`: minute
    * `h`: hour
    * `d`: day
    * `mon`: month

---
