# Encoding and decoding

M42PL process _events_, which conveys any kind of data: text, number, bytes,
etc.

Although events can be constructed from nearly anything, it may be required
to _decode_ a source payload to work on it, and to _encode_ an event or an
event field to pass it to another system.

## Codecs

The command `codecs` yields the available _codecs_, i.e. data encoders and
decoders.

You can use the codec' `alias` in the `encode` and `decode` commands.

```
| codecs
```

Example output:

```json
{
  "codec": {
    "alias": "json",
    "about": "Support for JSON text format"
  }
}

{
  "codec": {
    "alias": "hjson",
    "about": "Support for colored JSON text format"
  }
}

{
  "codec": {
    "alias": "msgpack",
    "about": "Support for MsgPack binary format"
  }
}
```

## Encoding

The `encode` command encodes an event or an event field with the given _codec_.

### Encode an event

Script:

```
| make showinfo=yes | encode dest='json' codec='json' | fields json
```

Variant syntax:

```
| make showinfo=yes | encode as json with 'json' | fields json
```

Output:

```json
{
  "json": "{\"id\": 0, \"chunk\": {\"chunk\": 0, \"chunks\": 1}, \"count\": {\"begin\": 0, \"end\": 1}, \"pipeline\": {\"name\": \"main\"}}"
}
```

### Encode a field

Script:

```
| make showinfo=yes | encode src=pipeline dest=json codec='json' | fields json
```

Variant syntax:

```
| make showinfo=yes | encode pipeline as json with 'json' | fields json
```

Output:

```json
{
  "json": "{\"pipeline\": {\"name\": \"main\"}}"
}
```

---

## Decoding

The `decode` command decodes an event field with the given _codec_.

!!! note "Examples are examples"
    The next example is trivial; a real world use case could be to send events
    through a socket or a queue system such as ZeroMQ, but this is out of this
    document scope.

First, lets created a _msgpack_-encoded field and get the encoded value:

```
| make showinfo=yes
| encode with 'msgpack'
| fields encoded
```

Then, lets decode the field `encoded` with the proper codec and keep only
the decoded event:

```
| decode "encoded" with msgpack
| fields - encoded
```

Output:

```json
{
  "id": 0,
  "chunk": {
    "chunk": 0,
    "chunks": 1
  },
  "count": {
    "begin": 0,
    "end": 1
  },
  "pipeline": {
    "name": "main"
  }
}
```

Complete script for reference:

```
| make showinfo=yes | encode with 'msgpack' | fields encoded 
| decode "encoded" with msgpack | fields - encoded
```

---
