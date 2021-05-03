Fields
======

M42PL fields are Python functors used to read and write events attributes.
Fields classes are derived from the base class
:class:`m42pl.fields.__base__.BaseField`.

Inheritance diagram
-------------------

.. inheritance-diagram:: m42pl.fields.dict
                         m42pl.fields.eval
                         m42pl.fields.json
                         m42pl.fields.literal
                         m42pl.fields.pipe
                         m42pl.fields.seqn
   :parts: 1

Field class anatomy
-------------------

A *field* class is a functor which extends the
:class:`m42pl.fields.__base__.BaseField` field.
