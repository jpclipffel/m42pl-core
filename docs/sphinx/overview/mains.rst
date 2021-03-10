Mains
=====

The :module:`m42pl.mains` implements M42PL command line entry points,
built using `argparse`.

The different entry points are referred as *actions* and must derive from one
of the following classes:

* :class:`m42pl.mains.__base__.RunAction` for actions running M42PL scripts
* :class:`m42pl.mains.__base__.DebugAction` for debug / hacks actions

Current inheritance diagram:

.. inheritance-diagram:: m42pl.mains.repl.REPL
                         m42pl.mains.run.Run
                         m42pl.mains.grammar.Grammar
   :parts: 1

Action class anatomy
--------------------

An *action* class is a functor which implements two methods:

.. code-block:: Python

    def __init__(self, *args, **kwargs) -> None:
        """Initializes the class and its parrent(s) class(es).
        """

.. code-block:: Python

    def __call__(self, args: 'argparse.Namespace') -> None:
        """Runs the action.

        :param args: Arguments map parsed by argparse
        """

The class should be located in `m42pl/mains/`, **preferably** in its own module
(e.g. `m42pl/mains/myaction.py`).

Action class behaviour
----------------------

.. code-block:: Python

    # Import either RunAction or DebugAction, not both
    from .__base__ import RunAction
    from .__base__ import DebugAction

    # Inherit from the imported action class
    class MyAction(RunAction):

        def __init__(self, *args, **kwargs):
            """Initializes the class and its parrent(s) class(es).
            """

            # Mandatory: The parent class must be initialized with the
            # action name, i.e, the command name as used in the command
            # line tool. Hereafter the name is set to 'myaction':
            super().__init__('myaction', *args, **kwargs)

            # Optional: Add parser arguments.
            # Refer to the 'argparse' module for the argument syntax:
            # https://docs.python.org/3/library/argparse.html
            self.parser.add_argument(
                'positional',
                help='Argument description'
            )
            self.parser.add_argument(
                '-o',
                '--optional',
                help='Argument description'
            )

        def __call__(self, args):
            """Runs the action.

            :param args: Arguments map parsed by argparse
            """
            # Mandatory: call the parent(s) class(es)
            super().__call__(args)
            # Action logic is defined here
            # ...
