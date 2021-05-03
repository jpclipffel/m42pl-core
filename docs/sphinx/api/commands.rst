Commands
========

.. autoclass:: m42pl.commands.__base__.Command
   :members:
   :inherited-members:
   :exclude-members: Transformer

.. autoclass:: m42pl.commands.__base__.AsyncCommand
   :members:
   :exclude-members: Transformer

.. autoclass:: m42pl.commands.GeneratingCommand
   :members:
   :special-members: __init__, __call__
   :exclude-members: Transformer

.. autoclass:: m42pl.commands.StreamingCommand
   :members:
   :special-members: __init__, __call__
   :exclude-members: Transformer

.. autoclass:: m42pl.commands.BufferingCommand
   :members:
   :special-members: __init__, __call__
   :exclude-members: Transformer

.. autoclass:: m42pl.commands.MetaCommand
   :members:
   :special-members: __init__, __call__
   :exclude-members: Transformer