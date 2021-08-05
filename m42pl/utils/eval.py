import ntpath
import regex
import os

from typing import Any

from .time import now, reltime, strftime, strptime


class Undefined:
    """Undefined value placeholder.

    To be returned by EvalNS when no matching field is found.
    """

    def __getitem__(self, *args):
        return self

    def __getattribute__(self, *args):
        return self

    def __getattr__(self, *args):
        return self


class EvalNS(dict):
    """Custom pseudo-dict to shadow `globals()` when using `eval`.
    
    This class provides the following properties:

    * Resolves attributes with a namespace-like syntax
      (e.g. `root.node.leaf`)
    * Resolves a limited subset of functions
    * Supports and extends operations on attributes
      (add, sub, div, mul, div, ...)
    """
    
    def __init__(self, name: str, functions: dict, fields: Any):
        """
        :param name:        Attribute name (may be empty, e.g. `""`)
        :param functions:   Functions dict (may be empty, e.g. `{}`)
        :param fields:      Attributes values dict
        """
        setattr(self, 'name', name)
        setattr(self, 'functions', functions)
        setattr(self, 'fields', fields)
    
    def __getitem__(self, name: str):
        """Returns the attribute :param:`name` from current namespace.

        :param name:                Attribute name

        :ivar str self_name:        Current object's name
        :ivar dict self_functions:  Current object's functions map
        :ivar dict self_fields:     Current object's fields map
        """
        # Set 'self' attributes
        self_name = super().__getattribute__('name')
        self_functions = super().__getattribute__('functions')
        self_fields = super().__getattribute__('fields')
        # Returns the requested nested fields
        if isinstance(self_fields, dict) and name in self_fields:
            return EvalNS(
                name=name,
                functions=self_functions,
                fields=self_fields[name]
            )
        # Returns the requested fields
        elif name == self_name:
            return self_fields
        # Returns the requested functions
        elif name in self_functions:
            return self_functions[name]
        else:
            return Undefined()

    def __getattribute__(self, name: str, *args):
        return super().__getattribute__('__getitem__')(name)

    def __getattr__(self, name: str, *args):
        return super().__getattribute__('__getitem__')(name)
    
    def __cast__(self, other):
        return type(other)(super().__getattribute__('fields'))
    
    def __add__(self, other):
        return super().__getattribute__('__cast__')(other) + other

    def __radd__(self, other):
        return other + super().__getattribute__('__cast__')(other)

    def __sub__(self, other):
        return super().__getattribute__('__cast__')(other) - other

    def __rsub__(self, other):
        return other - super().__getattribute__('__cast__')(other)

    def __mul__(self, other):
        return super().__getattribute__('__cast__')(other) * other

    def __rmul__(self, other):
        return other * super().__getattribute__('__cast__')(other)

    def __truediv__(self, other):
        return super().__getattribute__('__cast__')(other) / other

    def __rtruediv__(self, other):
        return other / super().__getattribute__('__cast__')(other)
    
    def __mod__(self, other):
        return super().__getattribute__('__cast__')(other) % other

    def __rmod__(self, other):
        return other % super().__getattribute__('__cast__')(other)

    def __eq__(self, other):
        return super().__getattribute__('__cast__')(other) == other

    def __req__(self, other):
        return other == super().__getattribute__('__cast__')(other)

    def __ne__(self, other):
        return super().__getattribute__('__cast__')(other) != other

    def __lt__(self, other):
        return super().__getattribute__('__cast__')(other) < other

    def __le__(self, other):
        return super().__getattribute__('__cast__')(other) <= other

    def __gt__(self, other):
        return super().__getattribute__('__cast__')(other) > other

    def __ge__(self, other):
        return super().__getattribute__('__cast__')(other) >= other


def solve(attr, types: tuple = (), *args):
    """Resolves an attribute returned by :class:`EvalNS`.

    :param attr:    Attribute to resolve
    :param types:   Accepted types list (toptional)
    :param *args:   Default value to return (optional)
    """
    # If the attribute is an EvalNS, continue the evalutation and
    # return the result.
    if isinstance(attr, EvalNS):
        return super(EvalNS, attr).__getattribute__('fields')
    # If the attribute match one of the expected types, return it.
    # Otherwise, return the default value `args[0]` or `None` if no
    # default is given.
    elif len(types):
        if isinstance(attr, types):
            return attr
        elif len(args):
            return args[0]
        else:
            return None
    # If the attribute is an `Undefined` or `None`, return the default value
    # `args[0]` or `None` if no default is given.
    elif isinstance(attr, Undefined):
        if len(args):
            return args[0]
        else:
            return None
    # If no expected types are given, returns the attribute.
    return attr


class Evaluator:
    """Evaluates a (simplified) Python expression.

    This class can be used in any M42PL command or tool which needs to
    evaluate a Python expression (e.g. `eval` and `where` commands, or
    the `eval` field type).

    :ivar functions:    Utility functions available to `eval` and
                        `EvalNS`
    """

    # Evaluation functions
    functions = {
        # Misc.
        'field':        lambda field, default = None: solve(field, (type(default),), default),
        'isnull':       lambda field: solve(field, [], None) is None,
        'isnotnull':    lambda field: solve(field, [], None),
        'coalesce':     lambda *fields: next(filter(None, [solve(field) for field in fields]), None),
        # Time
        'now':          lambda: now().timestamp(),
        'reltime':      lambda field: reltime(solve(field)).timestamp(),
        'strftime':     lambda field, format = '%c': strftime(solve(field), solve(format)),
        'strptime':     lambda field, format: strptime(solve(field), solve(format)),
        # Cast
        'tostring':     lambda field: str(solve(field)),
        'toint':        lambda field: int(solve(field)),
        'tofloat':      lambda field: float(solve(field)),
        # String
        'clean':        lambda field: ''.join(solve(field, (str,), '').split()),
        'split':        lambda field, needle: solve(field, (str,), '').split(solve(needle, (str,), '')),
        # List
        'list':         lambda *args: [solve(i) for i in args],
        'join':         lambda field, delimiter='': delimiter.join(solve(field, (list, tuple, str))),
        'slice':        lambda field, start, *end: len(end) and solve(field, (str, list, tuple), None)[start:end[0]] or solve(field, (str, list, tuple), None)[start:],
        'idx':          lambda field, position: solve(field, (str, list, tuple), None)[position],
        'length':       lambda field: len(solve(field, (str, list, tuple), '')),
        # Map
        'keys':         lambda field: list(solve(field, (dict,), {}).keys()),
        # Math
        'round':        lambda field, x: round(solve(field, (float, int), 0), x),
        'even':         lambda field: solve(field, (int, float), 0) % 2 == 0,
        'true':         lambda field: field == True,
        'false':        lambda field: field == False,
        # Filter
        'match':        lambda field, values: bool(list(filter(None, [ regex.findall(v, solve(field, (str,), '')) for v in isinstance(values, (list, tuple)) and values or (values,) ]))),
        # Path
        'basename':     lambda field: ntpath.basename(solve(field, (str,), 0)),
        'dirname':      lambda field: ntpath.dirname(solve(field, (str,), 0)),
        'joinpath':     lambda *args: os.path.join(*[solve(i) for i in args]),
        'cwd':          lambda: os.getcwd(),
    }
    
    # Evaluation functions aliases
    functions.update({
        # Misc
        'isnone':       functions['isnull'],
        'isnotnone':    functions['isnotnull'],
        # String
        'str':          functions['tostring'],
        'string':       functions['tostring'],
        # List
        'at':           functions['idx'],
        'len':          functions['length'],
        # Path
        'makepath':     functions['joinpath'],
        'workdir':      functions['cwd'],
    })
    
    def __init__(self, expression: str):
        """
        :param expression:  Python expression to evaluate
                            This expression may uses the functions
                            defined in `Evaluator.functions`
        """
        # Pre-compile the expression
        self.compiled = compile(
            source=expression,
            filename='<string>',
            mode='eval'
        )

    def __call__(self, data: dict = {}) -> Any:
        """Runs evaluation and returns its result.

        :param data:    Event's data used as eval's globals
        """
        # Build environement (functions map and globals)
        env = EvalNS(name='', functions=self.functions, fields=data)
        # Evaluate the pre-compiled expression using built env
        evaluated = eval(self.compiled, env)
        # Solve the result a last time as EvalNS may returns a nested EvalNS
        solved = solve(evaluated, [], None)
        # Done
        return solved
