import functools

from easyvalidate._helpers import get_argument_dict, get_argument_names


def validate_range(**ranges):
    """Decorator for making sure that values passed to a function are
    in an appropriate range.

    Takes keyword arguments of `ARG_NAME=(LOWER, UPPER)`.

    Raises:
        NameError if one or more arguments specified do not exist in the function
            signature.
        TypeError if the range specified for an argument is not a list or tuple of numbers.
        ValueError if the range does not have length 2 (lower and upper bounds).
    """
    def outer(func):
        arg_names = get_argument_names(func)
        for arg_name, range in ranges.items():
            if arg_name not in arg_names:
                raise NameError(f'Cannot specify range for non-existent argument "{arg_name}".')
            if not isinstance(range, (list, tuple)):
                raise TypeError(f'Range for "{arg_name}" must be a list or tuple, not {type(range).__name__}.')
            if len(range) != 2:
                raise ValueError(f'Range for "{arg_name}" is the wrong size, must be length 2.')
            if not all(isinstance(x, (int, float)) for x in range):
                raise TypeError(f'Range for "{arg_name}" must contain only numbers.')

            lower, upper = range[0], range[1]
            ranges[arg_name] = min(lower, upper), max(lower, upper)

        @functools.wraps(func)
        def inner(*args, **kwargs):
            all_args = get_argument_dict(arg_names, args, kwargs)

            for arg_name, range in ranges.items():
                given_value = all_args[arg_name]
                try:
                    if not range[0] <= given_value <= range[1]:
                        raise ValueError(f'Value for "{arg_name}" must be in the range [{range[0]}, {range[1]}], but got {given_value}.')
                except TypeError:
                    raise TypeError(f'Cannot validate the range of argument "{arg_name}", as it is non-numeric.')

            return func(*args, **kwargs)
        return inner
    return outer
