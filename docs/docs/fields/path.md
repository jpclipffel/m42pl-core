<!-- vim: set ft=Markdown ts=4 -->

# Path fields

Path fields are event's attributes names, which may use a dotted notattion
(e.g. `some.field.name`) to represent nested events fields.

## Syntax

* Root fields are written as-in, e.g. `fieldName`
* Nested fields are sperated by a dot, e.g. `user.name`, `user.identity.name`
* Fields with spaces in their name can may be encosed in double-quotes, e.g. `"user name"`, `"user.last name"`

!!! warning "Quotes matters"
    Enclosing a fields into single-quotes as `'some string'` as a different
    meaning: see [literal fields](./literal.md)

## Examples

### Generate fields

```
| make
| eval
    userid = 'jdoe',
    user.name = 'John',
    user.lastname = 'Doe',
    "user.twitter account" = "@JDoe",
    user.loc = list(1, 2, 3)
```

```json
{
  "userid": "jdoe",
  "user": {
    "name": "John",
    "lastname": "Doe",
    "twitter account": "@JDoe"
  }
}
```
