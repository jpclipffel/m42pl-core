<!-- vim: set ft=Markdown ts=4 -->

# Literal fields

Literal fields are literal values, which **are not** read from the events.
You can use literal fields to configure static commands values.

## Syntax

* Strings are enclosed in **simple quotes**, e.g. `'a string'`
* Numbers (integer or floats) are written as-is, e.g. `42`, `21.42`

!!! warning "Quotes matters"
    Enclosing a string into double-quotes as `"some string"` as a different
    meaning: see [path fields](./path.md)

## Examples

### Generate 2 events

```
| make count=2
```

* `2` is a literal value, interpreted as in integer

```json
{}

{}
```

### Query an URL

```
| url 'https://api.ipify.org'
```

* `'https://api.ipify.org'` is a literal value, interpreted as a string

```json
{
  "time": 1234,
  "request": {
    "method": "GET",
    "url": "https://api.ipify.org",
    "headers": {},
    "data": {}
  },
  "response": {
    "status": 200,
    "reason": "OK",
    "mime": {
      "type": "text/plain"
    },
    "headers": {
      "Server": "Cowboy",
      "Connection": "keep-alive",
      "Content-Type": "text/plain",
      "Vary": "Origin",
      "Date": "....",
      "Content-Length": "13",
      "Via": "1.1 vegur"
    },
    "content": "..."
  }
}
```

---
