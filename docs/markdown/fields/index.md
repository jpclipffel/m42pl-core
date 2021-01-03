---
layout: default
title: Fields
nav_order: 1
parent: M42PL
has_children: true
---

# Fields

Fields are the way M42PL read and write **events attributes**.

In M42PL, each **event** is a comparable to a **JSON document**. Both are
keys / values structures which contains keys of various types:

* String: A single value enclosed in double quotes: `"key": "a string"`
* Number: A number with or without a floating part: `"key": 42`, `"key": 42.21`
* Array: A sequence of sub-keys enclosed in square brackets: `"key": ["text data", 42, 42.21, {"key": "value"}]`
* Map: A structure of sub-keys encolsed in brackets: `"key": { "name": "some data" }`

M42PL provides multiple **fielsd solver** to easily read and write fields in
events. The syntax you use 

| Field type | Field example | Field solver |
|------------|---------------|--------------|
| Variable   | `key`         | `BaseField`  |
| String     | `"string"`    | `BaseField`  |

The following JSON document serves as an example to explain how fields
works in M42PL:

```json
{
    "name": "A JSON document",
    "properties": {
        "mime": "application/json",
        "keywords": ["json", "m42pl", "example"],
    },
    "children": [
        {
            "name": "First child",
            "properties": {
                "keywords": ["child", "first"]
            }
        },
        {
            "name": "Second child",
            "properties": {
                "keywords": ["child", "second"]
            }
        }
    ]
}
```

