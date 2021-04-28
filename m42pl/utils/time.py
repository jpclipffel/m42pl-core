import regex
import datetime

from typing import Union


# Relative time units
RELTIME_UNITS = [
    'ms',
    's',
    'm',
    'h',
    'd'
]

# Relative time regex
RELTIME_REGEX = regex.compile((
    fr'(?P<sign>(-|\+)){{0,1}}'
    fr'(?P<req_value>[0-9]+)'
    fr'(?P<req_unit>({"|".join(RELTIME_UNITS)})){{1}}'
    '@'
    fr'(?P<ref_unit>({"|".join(RELTIME_UNITS)}|now)){{1}}'
))

# Rounding values
ROUND_VALUES = {
    's':   {'microsecond': 0},
    'm':   {'microsecond': 0, 'second': 0},
    'h':   {'microsecond': 0, 'second': 0, 'minute': 0},
    'd':   {'microsecond': 0, 'second': 0, 'minute': 0, 'hour': 0},
}

# Delta values
DELTA_VALUES = {
    'ms': '',
    's':  'seconds',
    'm':  'minutes',
    'h':  'hours',
    'd':  'days',
}


def now() -> datetime.datetime:
    """Returns the current time.
    """
    return datetime.datetime.now()


def round(dt, unit: str) -> datetime.datetime:
    """Rounds the given datetime instance to the given unit.

    :param dt:      Datetime instance
    :param unit:    Unit to round to
    """
    return dt.replace(**ROUND_VALUES.get(unit, {}))


def reltime(expression: str) -> datetime.datetime:
    """Evaluates a relative time expression adn returns its time.

    :param expression:  Relative time expression
                        Format is "(+|-)<value><unit>@<precision>"
    """
    # Parse relative time expression
    rx = RELTIME_REGEX.match(expression)
    # Round reference time (== current time) to reference unit
    ref_time = round(datetime.datetime.now(), rx.group("ref_unit"))
    # Extract relative time value and unit
    req_value, req_unit = float(rx.group("req_value")), rx.group("req_unit")
    # Return reference time - relative time
    if req_unit == "ms":
        return ref_time - datetime.timedelta()
    return ref_time - datetime.timedelta(**{DELTA_VALUES[req_unit]: req_value})


# pylint: disable=unsubscriptable-object
def strftime(expression: Union[float, str], format: str) -> str:
    """Returns a string representation of the given time expression.

    :param expression:  Time as epoch (Float) or relative time (String)
    :param format:      Standard strftime format string
    """
    if isinstance(expression, float):
        return datetime.datetime.fromtimestamp(expression).strftime(format)
    else:
        if expression.lower() == 'now':
            return datetime.datetime.now().strftime(format)
        return reltime(expression).strftime(format)
