import regex
import datetime
from dateutil.relativedelta import relativedelta

from typing import Union


# Relative time units
RELTIME_UNITS = [
    'mon',  # month
    'ms',   # micro second
    's',    # second
    'm',    # minute
    'h',    # hour
    'd',    # day
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
    's':    {'microsecond': 0},
    'm':    {'microsecond': 0, 'second': 0},
    'h':    {'microsecond': 0, 'second': 0, 'minute': 0},
    'd':    {'microsecond': 0, 'second': 0, 'minute': 0, 'hour': 0},
    'w':    {'microsecond': 0, 'second': 0, 'minute': 0, 'hour': 0, 'day': 1},
    'mon':  {'microsecond': 0, 'second': 0, 'minute': 0, 'hour': 0, 'day': 1},
}

# Delta values
DELTA_VALUES = {
    'ms':   '',
    's':    'seconds',
    'm':    'minutes',
    'h':    'hours',
    'd':    'days',
    'mon':  'months'
}


def now() -> datetime.datetime:
    """Returns the current time.
    """
    return datetime.datetime.now()


def round(dt, unit: str) -> datetime.datetime:
    """Rounds the given datetime instance to the given unit.

    :param dt: Datetime instance
    :param unit: Unit to round to
    """
    return dt.replace(**ROUND_VALUES.get(unit, {}))


def reltime(expression: str, dt = None) -> datetime.datetime:
    """Evaluates a relative time expression and returns its time.

    Relative time expression is "(+|-)<value><unit>@<precision>"

    :param expression: Relative time expression
    """
    # Parse relative time expression
    rx = RELTIME_REGEX.match(expression)
    # Round reference time (== current time) to reference unit
    ref_time = round(dt or datetime.datetime.now(), rx.group('ref_unit'))
    # Extract relative time value and unit
    req_value, req_unit = float(rx.group('req_value')), rx.group('req_unit')
    # Get relative time
    if req_unit == 'ms':
        rel_time = datetime.timedelta()
    else:
        # rel_time = datetime.timedelta(**{DELTA_VALUES[req_unit]: req_value})
        rel_time = relativedelta(**{DELTA_VALUES[req_unit]: req_value})
    # Return reference time -/+ relative time
    if rx.group('sign') in [None, '-']:
        return ref_time - rel_time
    else:
        return ref_time + rel_time


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


def strptime(expression, format: str):
    """Returns an epoch float from the given formated time string.

    :param expression: Time as string
    :format: Time string format
    """
    return datetime.datetime.strptime(expression, format).timestamp()
