Fields
======

M42PL fields are Python functors which are used to read and write events
attributes. Fields classes are derived from the base class
:py:class:`m42pl.fields.__base__.BaseField`.

Inheritance diagram
-------------------

.. inheritance-diagram:: m42pl.fields.dict
                         m42pl.fields.eval
                         m42pl.fields.json
                         m42pl.fields.literal
                         m42pl.fields.pipe
                         m42pl.fields.seqn
   :parts: 1

---

Field class anatomy
-------------------

A *field* class is a functor which extends the
:py:class:`m42pl.fields.__base__.BaseField` field.

It should implements the following methods:

Init
^^^^

The :py:meth:`__init__` method initializes the field and its parent class.
It should at least take a ``name`` parameter which is the field name and, if
the field is a lteral (string or number), also the field value.

.. code-block:: Python

    def __init__(self, name, default = None, type = None, seqn = False):
        super().__init__(*args, **kwargs)
        # ...

.. autofunction:: m42pl.fields.__base__.BaseField.__init__

Read
^^^^

The :py:meth:`_read` method reads and returns the field value from the given
``event`` and ``pipeline``.

This method is asynchronous since some fields may relies on complex mechanisms
to get their values: running a sub-pipeline, evaluating expressions, querying a
dataset, etc.

.. note:: The method name to implement is ``_read`` (with and underscore) and
   **not** ``read``; ``read`` is a parent class mwthod which will properly call
   the field method and ensure the results is well-formatted.

.. code-block:: Python

    async def _read(self, event, pipeline):
        # ...

.. autofunction:: m42pl.fields.__base__.BaseField._read

Write
^^^^^

The :py:meth:`_write` method writes (update / set) and returns the field value
from the given ``event`` and ``value``.

This method is asynchronous since some fields may relies on complex mechanisms
to set their values: running a sub-pipeline, evaluating expressions, querying a
dataset, etc.

.. note:: The method name to implement is ``_write`` (with and underscore) and
   **not** ``write``; ``write`` is a parent class mwthod which will properly
   call the field method and ensure the results is well-formatted.

.. warning:: It may be legitimate to not implement this method if it does not
   make any sense: for instance, one cannot `write` to a sub-pipeline nor to an
   evaluated expression.

.. code-block:: Python

    async def _write(self, event, value):
        # ...

.. autofunction:: m42pl.fields.__base__.BaseField._write

Delete
^^^^^^

The :py:meth:`_delete` method removes the field value from the given ``event``.

This method is asynchronous since some fields may relies on complex mechanisms
to remove their values: running a sub-pipeline, evaluating expressions,
querying a dataset, etc.

.. note:: The method name to implement is ``_delete`` (with and underscore) and
   **not** ``delete``; ``delete`` is a parent class mwthod which will properly
   call the field method and ensure the results is well-formatted.

.. warning:: It may be legitimate to not implement this method if it does not
   make any sense: for instance, one cannot `delete` from a sub-pipeline nor
   from an evaluated expression.

.. code-block:: Python

    async def _delete(self, event):
        # ...

.. autofunction:: m42pl.fields.__base__.BaseField._delete
