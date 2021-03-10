Commands
========

M42PL commands are Python functors (classes implementing a `__call__` method)
derived from one of the fundamental classes defined in `m42pl.commands` module:

* :class:`m42pl.commands.GeneratingCommand`
* :class:`m42pl.commands.StreamingCommand`
* :class:`m42pl.commands.BufferingCommand`
* :class:`m42pl.commands.MergingCommand`
* :class:`m42pl.commands.MetaCommand`

.. note:: Commands classes are imported by :code:`m42pl.commands`'s :code:`__init__.py`

.. inheritance-diagram:: m42pl.commands.GeneratingCommand 
                         m42pl.commands.StreamingCommand
                         m42pl.commands.MergingCommand
                         m42pl.commands.MetaCommand
                         m42pl.commands.BufferingCommand
   :parts: 1

Command class anatomy
---------------------

To do.

Implement a new generating command
----------------------------------

To do.

Implement a new streaming command
---------------------------------

To do.

Implement a new buffering command
---------------------------------

To do.

Implement a new meta command
----------------------------

To do.
