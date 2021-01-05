from collections import defaultdict
from textwrap import dedent
import ntpath
import regex

from typing import Any

from .time import now, reltime, strftime


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
    
    * Resolves attributes with a namespace-like syntax
      (e.g. `root.node.leaf`)
    * Resolves a limited subset of functions
    * Supports and extends operations on attributes
      (add, sub, div, mul, div, ...)
    """
    
    def __init__(self, name: str, functions: dict, fields: Any):
        """
        :param name:        Attribute name; May be empty (`""`).
        :param functions:   Functions dict; May be empty (`{}`).
        :param fields:      Attributes values dict.
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
        self_name = super().__getattribute__('name')
        self_functions = super().__getattribute__('functions')
        self_fields = super().__getattribute__('fields')
        
        if name in self_functions:
            # print(f'EvalNS({self_name}).__getitem__({name}) --> function[{name}]')
            return self_functions[name]
        elif isinstance(self_fields, dict) and name in self_fields:
            # print(f'EvalNS({self_name}).__getitem__({name}) --> EvalNS(name={name}, fields=self.fields[{name}])')
            return EvalNS(name=name, functions=self_functions, fields=self_fields[name])
        elif name == self_name:
            # print(f'EvalNS({self_name}).__getitem__({name}) --> self.fields')
            return self_fields
        else:
            # print(f'EvalNS({self_name}).__getitem__({name}) --> Unexistent')
            return Undefined()
            # print(f'EvalNS({self_name}).__getitem__({name}) --> None')
            # raise Exception(f'TEST EXCEPTION -- EvalNS({self_name}).__getitem__({name}) --> None')
            # return self

    def __getattribute__(self, name: str, *args):
        # print(f'EvalNS.__getattribute__({name}) --> self.__getitem__({name})')
        return super().__getattribute__('__getitem__')(name)

    def __getattr__(self, name: str, *args):
        # print(f'EvalNS.__getattr__({name}) --> self.__getitem__({name})')
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


def solve(attr, types: list = [], *args):
    """Resolves an attribute returned by :class:`EvalNS`.

    :param attr:    Attribute to resolve.
    :param types:   Accepted types list (toptional).
    :param *args:   Default value to return (optional).
    """
    # print(f'solve() --> {attr}, {types}, {args}')
    # If the attribute is an EvalNS, continue the evalutation and
    # return the result.
    if isinstance(attr, EvalNS):
        return super(EvalNS, attr).__getattribute__('fields')
    # If attribute match one of the expected types, return it.
    # Otherwise, return the default value `args[0]` or None if no
    # default is given.
    elif len(types):
        if type(attr) in types:
            return attr
        elif len(args):
            return args[0]
        else:
            return None
    # If no expected types are given, returns the attribute.
    return attr


class Evaluator:
    """Evaluates a (simplified) Python expression.

    This class can be used in any M42PL command or tool who needs to
    evaluate a Python expression (e.g. `eval` and `where` commands, or
    the `eval` field type).

    :ivar function: Utility functions available to `eval` and `EvalNS`.
    """

    # Evaluation functions
    functions = {
        # Misc.
        'field':        lambda field, default = None: solve(field, [type(default), ], default),
        # Time
        'now':          lambda: now().timestamp(),
        'reltime':      lambda expression: reltime(expression).timestamp(),
        'strftime':     lambda expression, format: strftime(expression, format),
        # Cast
        'tostring':     lambda field: str(solve(field)),
        'toint':        lambda field: int(solve(field)),
        'tofloat':      lambda field: float(solve(field)),
        # String
        'basename':     lambda field: ntpath.basename(solve(field, [str, ], 0)),
        'dirname':      lambda field: ntpath.dirname(solve(field, [str, ], 0)),
        'clean':        lambda field: ''.join(solve(field, [str,], '').split()),
        # List
        'list':         lambda *args: [solve(i) for i in args],
        'join':         lambda field, delimiter='': delimiter.join(solve(field, [list, tuple, str, ])),
        'slice':        lambda field, start, *end: len(end) and solve(field, [str, list, tuple, ], None)[start:end[0]] or solve(field, [str, list, tuple, ], None)[start:],
        'index':        lambda field, position: solve(field, [str, list, tuple, ], None)[position],
        'length':       lambda field: len(solve(field, [str, list, tuple], '')),
        # Math
        'round':        lambda field, x: round(solve(field, [float, int, ], 0), x),
        'even':         lambda field: solve(field, [int, float], 0) % 2 == 0,
        'true':         lambda field: field == True,
        'false':        lambda field: field == False,
        # Filter
        'match':        lambda field, values: bool(list(filter(None, [ regex.findall(v, solve(field, [str, ])) for v in values ]))),
    }
    
    # Evaluation functions aliases
    functions.update({
        # String
        'str':      functions['tostring'],
        'string':   functions['tostring'],
        # List
        'at':       functions['index'],
        'len':      functions['length'],
    })
    
    def __init__(self, expression: str):
        """
        :param expression:  Python expression to evaluate.
                            This expression may uses the functions
                            defined in `Evaluator.functions`.
        """
        # Pre-compile the expression
        self.compiled = compile(
            source=expression,
            filename='<string>', 
            mode='eval'
        )

    def __call__(self, data: dict = {}):
        """Run evaluation.

        :param data:    Events fields (`event.data`).
                        Will be used as eval's `global`.
        """
        # ---
        # Build environement (functions map and globals)
        env = EvalNS(name='', functions=self.functions, fields=data)
        # ---
        # Evaluate the pre-compiled expression using built env
        # print(f'Evaluator --> evaluating')
        evaluated = eval(self.compiled, env)
        # print(f'Evaluator --> evaluated --> {evaluated}')
        # ---
        # Solve the result a last time as EvalNS may returns a nother EvalNS
        # print(f'Evaluator --> solving')
        solved = solve(evaluated, [], None)
        # print(f'Evaluator --> solved --> {solved}')
        # ---
        # Done
        return solved
