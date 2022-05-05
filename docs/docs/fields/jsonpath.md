<!-- vim: set ft=Markdown ts=4 -->

# JsonPath fields

JsonPath fields extract a field's value from an event using a JsonPath
expression.

JsonPath syntax reference:

* [https://pypi.org/project/jsonpath-ng/](https://pypi.org/project/jsonpath-ng/)
* [https://goessner.net/articles/JsonPath/](https://goessner.net/articles/JsonPath/)

## Syntax

JsonPath fields are enclosed in brackets:

```
field={a.b.c[0]}
```

## Example

```
| make
| eval mpl.encoders = list('raw', 'json')
| rename {mpl.encoders[0]} as encoders
```

* `{mpl.encoders[0]}` is a JsonPath expression which selects the first
  item (`[0]`) of the nested field `encoders` in the root field `mpl`.

```json
{
  "mpl": {
    "encoders": [
      "json"
    ]
  },
  "encoders": "raw"
}
```
