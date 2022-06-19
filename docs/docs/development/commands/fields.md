<!-- vim: set ft=Markdown ts=4 -->

# Fields

An M42PL command's class arguments are used to configured the commands fields.

M42PL provide two base classes to interact with the pipelines fields:

* `m42pl.fields.Field`: read/write a single field
* `m42pl.fields.FieldsMap`: read multiple fields

## Field

The class `m42pl.field.Field` takes 4 arguments:

| Name      | Type                          | Default | Description                                           |
| --------- | ----------------------------- | ------- | ----------------------------------------------------- |
| `name`    | `str`, `Any`                  | -       | Field name or literal value                           |
| `default` | `Any`                         | `None`  | Default value if the field is not found               |
| `type`    | `type`, `tuple[type]`, `None` | `None`  | Allowed type for the field's value                    |
| `seqn`    | `bool`                        | `False` | Force the field's value to be wrapped into a sequence |

The following schema shows how a field is read and processed:

![Fields reading](/assets/fields_reading.png){ align=left }

## FieldsMap

To do.

## Example

```python
class MyCommand(StreamingCommand):

    _aliases_ = ['my-command',]

    def __init__(self, static: str, dynamic: str = 'example.dynamic'):
        super().__init__(static, dynamic)
        self.static = Field(static)
        self.dynamic = Field(dynamic)

    async def setup(self, event, pipeline, context):
        self.static_value = await self.static.read(event, pipeline, context)
    
    async def target(self, event, pipeline, context):
        dynamic_value = await self.dynamic.read(event, pipeline, context)
        yield event
```

Let's start with the basic:

* `static` is a required argument
* `dynamic` is an optional argument with the default value `example.dynamic`
* `MyCommand.static` and `MyCommand.dyanmic` are both `Field` instances
* `MyCommand.static` and `MyCommand.dyanmic` will both read their values from an _event_

Now for the fields behaviour:

* `MyCommand.static` will read the value of the event's field name pointed by the argument `static`
* `MyCommand.static` will be read **once**, in `MyCommand.setup`
* `MyCommand.dynamic` will read the value of the event's field name pointed by the argument `dynamic`
* `MyCommand.dynamic` will be read **for each event**, in `MyCommand.target`


Assuming the following script and event:

```
| my-command example.static
```

```json
{
    "example": {
        "static": "foo",
        "dynamic": 42
    }
}
```

We get the following table:

| Kind           | Name      | Value             | Configured by          |
| -------------- | --------- | ----------------- | ---------------------- |
| Class argument | `static`  | `example.satic`   | Command parser         |
| Class argument | `dynamic` | `example.dynamic` | Argument default value |
| Field          | `static`  | `"foo"`           | Event                  |
| Field          | `dynamic` | `42`              | Event                  |


---
