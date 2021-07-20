from typing import Any
import pkg_resources
import regex


# Grok expression regex
RX_GROK = regex.compile((
    r'(%{'
        r'(?<pattern>[a-zA-Z0-9_\.-]*)'
        r'(:(?<name>[a-zA-Z0-9_\.-]*))?'
        r'(:(?<rules>[a-zA-Z0-9_,-]*))?'
    r'})'
))

# Grok patterns definition regex
RX_DEFINITION = regex.compile(
    r'^(?<pattern>[a-zA-Z0-9_\.-]+)\s+(?<expression>.*)$'
)

# Parsed Grok patterns
PATTERNS = {} # type: dict[str, str]

# Grok rules
RULES = {
    'str':      lambda x: str(x),
    'int':      lambda x: int(x),
    'float':    lambda x: float(x),
    'upper':    lambda x: str.upper(x),
    'lower':    lambda x: str.lower(x),
    'list':     lambda x: list(x)
}


def parse_grok(expression: str, nested_sep: str = '__',
                keep_nameless: bool = False) -> tuple[str, dict[str, list[str]]]:
    """Translates a Grok expression to a regex.

    Returns a regular expression as a string and a mapping of the regex
    groups name and their associated rules.

    :param expression:      Grok expression
    :param nested_sep:      Nested fields separator (replaces `a.b`
                            with `a<sep>b`)
    :param keep_nameless:   Keep the nameless group and name them
                            after their Grok pattern name
    """
    rules = {} # type: dict[str, list[str]]
    for group in RX_GROK.findall(expression):
        # Extract Grok group properties
        grok_expression = group[0]
        grok_pattern = group[1]
        grok_field = group[3].replace('.', nested_sep)
        grok_rules = list(filter(None, group[5].split(','))) # type: ignore
        # Set Grok field name and rules
        if len(grok_field) >= 1:
            rx_group_name = f'?<{grok_field}>'
            rules[grok_field] = grok_rules
        elif keep_nameless:
            rx_group_name = f'?<{grok_pattern}>'
            rules[grok_pattern] = grok_rules
        else:
            rx_group_name = ''
        # Update internal regex translated from Grok
        expression = expression.replace(
            grok_expression,
            f'({rx_group_name}{PATTERNS[grok_pattern]})'
        )
    # Done
    return expression, rules


def load_grok(path: str):
    """Loads a set of Grok expression from a file.

    The functions has a very limited support for pattern referenced
    before definition: all patterns failed to parse during the first
    cycle are retried a second time.

    :param path:    Path to a file which contains Grok patterns
    """
    failed = []
    with open(path, 'r') as fd:
        for line in fd:
            match = RX_DEFINITION.match(line)
            if match:
                try:
                    pattern, expression = match.groupdict().values()
                    PATTERNS[pattern] = parse_grok(expression)[0]
                except Exception:
                    failed.append((pattern, expression))
    # Retry failed patterns 
    for pattern, expression in failed:
        try:
            PATTERNS[pattern] = parse_grok(expression)[0]
        except Exception:
            pass


# Load default Grok patterns
load_grok(pkg_resources.resource_filename('m42pl', "files/grok_patterns"))


class GrokRuleError(Exception):
    """Exception raised when a Grok rule fails or is not found.
    """
    
    def __init__(self, rule: str, message: str = ''):
        super().__init__(f'{rule}: {message}')


class Grok:
    """A simple Grok implementation.

    :ivar rx:       Regular expression built from a Grok expression
    :ivar groups:   Grok expression's groups rules & misc
    """

    def __init__(self, expression: str, nested_sep: str = '__', keep_nameless: bool = False, ignore_failed: bool = False):
        """
        :param expression:      Grok expression
        :param nested_sep:      Nested fields separator (replaces `a.b`
                                with `a<sep>b`)
        :param keep_nameless:   Keep the nameless group and name them
                                after their Grok pattern name
        :param ignore_failed:   If True, ignore errors and return
                                as much as possible fields
        """
        self.nested_sep = nested_sep
        self.keep_nameless = keep_nameless
        self.ignore_failed = ignore_failed
        # Parse the Grok expression, set rules and compile regex
        rx, self.rules = parse_grok(expression, self.nested_sep, self.keep_nameless)
        self.rx = regex.compile(rx)

    def match(self, data: str) -> dict:
        """Matches the given data with the internal Grok expression.

        :param data:    Data to match with the internal Grok expression
        """
        res = {}
        matched = self.rx.match(data)
        if matched is not None:
            for group, value in matched.groupdict().items():
                if len(self.rules.get(group, '')) > 0:
                    try:
                        for rule_name in self.rules[group]:
                            res[group] = RULES[rule_name](value)
                    except KeyError:
                        if not self.ignore_failed:
                            raise GrokRuleError(
                                rule_name,
                                f'Rule "{rule_name}" is not defined') from None
                    except Exception as error:
                        if not self.ignore_failed:
                            raise GrokRuleError(
                                rule_name,
                                str(error)) from None
                else:
                    res[group] = value
        return res

    def __call__(self, data: str) -> dict:
        return self.match(data)


if __name__ == '__main__':
    gk = Grok(
        '%{USER:user_name:str} is %{INT:user_age:float} and at %{EMAILADDRESS::lower}',
        keep_nameless=True,
        ignore_failed=False)
    print(
        gk.match('jpc is 27 and at jp.clipffel@protonmail.com')
    )
