import re
import datetime

from typing import Union


RELTIME_UNITS = [ 'ms', 's', 'm', 'h', 'd', 'mon', ]
RELTIME_REGEX = re.compile(fr'(?P<sign>(-|\+)){{0,1}}(?P<req_value>[0-9]+)(?P<req_unit>({"|".join(RELTIME_UNITS)})){{1}}@(?P<ref_unit>({"|".join(RELTIME_UNITS)}|now)){{1}}')


def now():
    return datetime.datetime.now()


def round(dt, unit: str):
    if unit == "ms":
        return dt
    elif unit == "s":
        return dt.replace(microsecond=0)
    elif unit == "m":
        return dt.replace(microsecond=0, second=0)
    elif unit == "h":
        return dt.replace(microsecond=0, second=0, minute=0)
    elif unit == "d":
        return dt.replace(microsecond=0, second=0, minute=0, hour=0)
    elif unit == "mon":
        return dt.replace(microsecond=0, second=0, minute=0, hour=0, day=1)


def reltime(expression: str):
    '''Evaluates and returns a *relative time expression*.
    '''

    rx = RELTIME_REGEX.match(expression)
    print(f'reltime: {RELTIME_REGEX} --> {rx}')

    ref_time = round(datetime.datetime.now(), rx.group("ref_unit")) # type: ignore
    
    req_value, req_unit = float(rx.group("req_value")), rx.group("req_unit") # type: ignore
    print(ref_time, req_value, req_unit)

    if req_unit == "ms":
        req_time = datetime.timedelta()
    elif req_unit == "s":
        req_time = datetime.timedelta(seconds=req_value) # type: ignore
    elif req_unit == "m":
        req_time = datetime.timedelta(minutes=req_value) # type: ignore
    elif req_unit == "h":
        req_time = datetime.timedelta(hours=req_value) # type: ignore
    elif req_unit == "d":
        req_time = datetime.timedelta(days=req_value) # type: ignore

    return ref_time - req_time


def strftime(expression: Union[float, str], format: str):
    if isinstance(expression, float):
        return datetime.datetime.fromtimestamp(expression).strftime(format)
    else:
        print(f'----> {expression}')
        if expression.lower() == 'now':
            return datetime.datetime.now().strftime(format)
        return reltime(expression).strftime(format)
