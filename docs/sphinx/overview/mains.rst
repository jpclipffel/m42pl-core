Mains
=====

The module :py:mod:`m42pl.mains` implements M42PL command line entry points,
built using :py:mod:`argparse`.

The different entry points are referred as `actions` and must derive from one
of the following classes:

* :py:class:`m42pl.mains.__base__.RunAction` to run M42PL scripts, REPL, ...
* :py:class:`m42pl.mains.__base__.DebugAction` for debug, hack, ...

Inheritance diagram
-------------------

.. inheritance-diagram:: m42pl.mains.repl.REPL
                         m42pl.mains.run.Run
                         m42pl.mains.grammar.Grammar
                         m42pl.mains.parse.Parse
   :parts: 1

---

Action class anatomy
--------------------

An *action* class is a functor which implements at least two methods:

Init
^^^^

The :py:meth:`__init__` method should always ``init`` the parent class with
the `action` name.

.. code-block:: Python

    def __init__(self, *args, **kwargs) -> None:
        """Initializes the class and its parent(s) class(es).
        """
        super().__init__('action_name', *args, **kwargs)

Call
^^^^

The :py:meth:`__call__` method should always ``call`` the parent class first.

.. code-block:: Python

    def __call__(self, args: 'argparse.Namespace') -> None:
        """Runs the action.

        :param args: Arguments map parsed by argparse
        """
        super().__call__(args)


Implementing an action
----------------------

The new `action` module should be located in ``m42pl/mains/``, e.g. 
``m42pl/mains/myaction.py``).

Do not forget to ``import`` the action in :py:mod:`m42pl.mains.__init__`:

.. code-block:: Python

    from .myaction import MyAction

Boilerplate code:

.. code-block:: Python

    # Import either RunAction or DebugAction, not both
    from .__base__ import RunAction
    from .__base__ import DebugAction

    # Inherit from the imported action class
    class MyAction(RunAction):

        def __init__(self, *args, **kwargs):
            """Initializes the class and its parent(s) class(es).
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

            :param args:    Arguments map parsed by argparse
            """
            # Mandatory: call the parent class
            super().__call__(args)
            # Action logic is defined here
            # ...
