Commands
========

M42PL commands are Python functors derived from one of the fundamental classes
defined in the module :mod:`m42pl.commands`:

* :class:`m42pl.commands.GeneratingCommand`
* :class:`m42pl.commands.StreamingCommand`
* :class:`m42pl.commands.BufferingCommand`
* :class:`m42pl.commands.MergingCommand`
* :class:`m42pl.commands.MetaCommand`

Each command type specializes in a way to generate, gather and process events.

Inheritance diagram
-------------------

.. inheritance-diagram:: m42pl.commands.GeneratingCommand 
                         m42pl.commands.StreamingCommand
                         m42pl.commands.MergingCommand
                         m42pl.commands.MetaCommand
                         m42pl.commands.BufferingCommand
   :parts: 1

---

Command classes
---------------

.. toctree::
   :maxdepth: 2

   classes/generating
   classes/streaming
   classes/buffering
   classes/merging
   classes/meta

Patterns
--------

.. toctree::
   :maxdepth: 1
   
   composition
