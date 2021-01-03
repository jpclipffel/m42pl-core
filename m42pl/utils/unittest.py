import unittest
from textwrap import dedent
from collections import OrderedDict, namedtuple
from dataclasses import dataclass, field
import json
import jsonpath_ng

import m42pl


# TestScript = namedtuple('TestScript', [
#     'name',         # Test name
#     'source',       # M42PL source script
#     'expected',     # Expected results (list of events)
#     'fields_in'     # Filter out all but those fields
# ])


@dataclass
class TestScript:
    """Test case template.

    :ivar name:         Script name.
    :ivar source:       M42PL script source code.
    :ivar expected:     Expected results, in the form of list of
                        events.
    :ivar fields_in:    Filter out all fields but these ones from
                        the results.
    """

    name: str
    source: str
    expected: list
    fields_in: list = field(default_factory=list)
    fields_out: list = field(default_factory=list)


class Command:
    """Base unit test case class for M42PL commands.

    This class creates its subclasses tests methods. For each item in
    :ivar expected_success: and :ivar expected_failure:, a new
    test method is generated and added to the test case class.

    This class also implements some feneric tests methods which
    applies to any command.

    :ivar comand_alias:     Command name (alias) which is tested.
    :ivar script_begin:     M42PL script snippet to preppend to
                            the test script code. This attribute is
                            typically set by the unit test case class.
    :ivar script_end:       M42PL script snippet to append to
                            the test script code. This attribute is
                            typically set by the unit test case class.
    :ivar expected_success: Tests which **must** success.
    :ivar expected_failure: Tests which **must** fail.
    """

    command_alias = ''
    script_begin = ''
    script_end = ''
    expected_success = []
    expected_failure = []

    def __init_subclass__(cls):

        def new_testcase(test_script: TestScript):
            """Generic test case factory.

            Returns a new test case method from a :class:`TestScript`
            instance.
            """
            def testcase(self):
                """Tests command execution and results.

                This generic test case method performs the following
                operations and tests:

                * Generate the test case source script
                * Initialize M42PL
                * Run the previously generated source script
                * Assert the number of results match the expected
                * Assert the content of results
                """
                # ---
                # Generate the test case source script by merging the
                # test case class's script's snippets and the test
                # script code.
                source = dedent(f'''\
                    {cls.script_begin}
                    {test_script.source}
                    {cls.script_end}
                ''')
                # ---
                # Local copy the test script parameters
                expected = test_script.expected
                fields_in = test_script.fields_in
                fields_out = test_script.fields_out
                # ---
                # Initialize M42PL
                context = m42pl.command('script')(source=source)()
                dispatcher = m42pl.dispatcher('local_test')(context)
                # ---
                # Run the the test script
                results = dispatcher()
                # ---
                # Test results length
                self.assertEqual(len(results), len(expected))
                # ---
                # Test results content
                # Events are compared on-by-one with each other from
                # the results set and the expected set.
                for res, exp in zip(results, expected):
                    # Clean up all fields but the selected one
                    for dataset in (res, exp):
                        # Keep only fields named in fields_in
                        for field in [k for k, v in dataset.data.items() if k not in fields_in]:
                            dataset.data.pop(field)
                        # Remove fields named in fields_out
                        for field in fields_out:
                            dataset.data.pop(field)
                    # Assert JSON dumps of result and expected match
                    self.assertEqual(
                        json.dumps(res.data, sort_keys=True), 
                        json.dumps(exp.data, sort_keys=True)
                    )
            # ---
            # Return the generated test case function `testcase`
            return testcase

        # Generated tests methods
        for test_scripts in [cls.expected_success, cls.expected_failure]:
            for test_script in test_scripts:
                setattr(
                    cls, 
                    f'test_script_{test_script.name}', 
                    new_testcase(test_script)
                )

        # Initialize M42PL and setup command class only if we're
        # targetting a final test case class (having a command alias)
        if len(cls.command_alias):
            m42pl.load_modules()
            cls.command = m42pl.command(cls.command_alias)

    def test_about(self):
        """Tests if the command has a valid `_about_` attribute.
        """
        # pylint: disable=no-member
        self.assertGreaterEqual(
            len(self.command._about_),
            2,
            dedent('''\
                Command's `_about_` field must not be empty and 
                should provide a short description of the command.
                '''
            )
        )
    
    def test_syntax(self):
        """Tests if the command has a valid `_syntax_` attribute.
        """
        # pylint: disable=no-member
        self.assertGreaterEqual(
            len(self.command._syntax_),
            2,
            dedent('''\
                Command's `_syntax_` field mut not be empty and
                should provide the command syntax in a shell-like
                (or docopt-like) syntax.
            ''')
        )
    
    def test_type(self):
        """Tests if the command inherits from a supported base command.

        :ivar valid_types:  List of supported base command types.
        """
        valid_types = (
            m42pl.commands.GeneratingCommand,
            m42pl.commands.StreamingCommand,
            m42pl.commands.BufferingCommand,
            m42pl.commands.MergingCommand,
            m42pl.commands.MetaCommand
        )
        # pylint: disable=no-member
        self.assertTrue(
            issubclass(self.command, valid_types),
            dedent(f'''\
                Command should be an instance of 
                {" or ".join([i.__name__ for i in valid_types])}.
            ''')
        )
    
    def test_initsuper(self):
        """Tests if the command `init` its parent class.
        """
        # pylint: disable=no-member
        self.assertTrue(
            '__init__' in self.command.__init__.__code__.co_names,
            dedent(f'''\
                Command does not initialize parent class.
            ''')
        )


class GeneratingCommand(Command):
    """Unit test case class for generating command.
    """
    pass


class StreamingCommand(Command):
    """Unit test case class for streaming command.

    This class injects a default M42PL code snippet to generate one
    event for the command to process.

    :ivar script_begin: Default M42PL code snipped to append. This
                        snippet generate 1 (one) empty event.
    """
    script_begin = dedent('''\
        | make count=1 showinfo=no
    ''')
