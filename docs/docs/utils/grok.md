<!-- vim: set ft=Markdown ts=4 -->

# Grok

_Grok_ is a wrapper around regular expression, which provide a set of
ready-to-use _patterns_ which compiles into a standard regular expression.

General syntax is:

```
%{<PATTERN>[:name][:rule,...]}
```

Where:

* `<PATTERN>` is a Grok pattern name
* `[name]` is a field name, which defaults to `PATTERN`
* `[rule,...]` is one or more _rule_ to apply to the extrated value

!!! note "Comparison with Logstash's Grok filter"
    M42PL supports two additionals options:

    * `name` can refer to a nested field, such as `user.name`
    * One or more `rule` can be added after `name` to post-process the parsed
      value

## Example

Input:

```
userName="john" userID=42 action="login"
```

Grok expression:

```
userName="%{DATA:user.name}" userID=%{NUMBER:user.id:int} action="%{DATA:action.name}"
```

Result:

```json
{
  "user": {
    "name": "john",
    "id": 42
  },
  "action": {
    "name": "login"
  }
}
```

## Patterns

The default patterns are available here: [Repository](https://github.com/jpclipffel/m42pl-core/tree/main/m42pl/files/grok_patterns)

!!! warning "Pattern source"
    The author would like to inform that he copied the Grok patterns from the
    following repository some months ago, and did not manage to find back to
    original file to source it here: 
    [Repository](https://github.com/logstash-plugins/logstash-patterns-core)



## Rules

* `str`: Cast to a string
* `int`: Cast to an integer
* `float`: Cast to a float
* `upper`: Convert to uppercase
* `lower`: Convert to lowecase
* `list`: Convert to a list
