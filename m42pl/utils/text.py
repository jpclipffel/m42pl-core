str_bool_true = ('yes', 'true', 'on')
str_bool_false = ('no', 'false', 'off')


def str_to_bool(text: str, default: bool = False):
    if isinstance(text, str):
        if text.lower() in str_bool_true:
            return True
        elif text.lower() in str_bool_false:
            return False
    return default
