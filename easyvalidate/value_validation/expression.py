import functools

from easyvalidate._helpers import get_argument_dict, get_argument_names
from easyvalidate.exceptions import ExpressionError
from .lazy_evaluation import is_expression


def validate_expression(**expressions):
    """Decorator for making sure that values passed to a function meet
    a criteria specified by an arbitrary expression.

    Takes keyword arguments of `ARG_NAME=EXPRESSION`.

    Raises:
        NameError if one or more arguments specified do not exist in the function
            signature.
        TypeError if the values given are not expressions.
    """
    def outer(func):
        arg_names = get_argument_names(func)
        for arg_name, expression in expressions.items():
            if arg_name not in arg_names:
                raise NameError(f'Cannot specify range for non-existent argument "{arg_name}".')
            if not is_expression(expression):
                raise TypeError(f'Expression for "{arg_name}" must be an epxression, not {type(expression).__name__}.')

        @functools.wraps(func)
        def inner(*args, **kwargs):
            all_args = get_argument_dict(arg_names, args, kwargs)

            for arg_name, expression in expressions.items():
                given_value = all_args[arg_name]
                try:
                    is_valid = expression.substitute(given_value)
                except Exception:
                    raise
                if not is_valid:
                    raise ValueError(f'Value for "{arg_name}" ({given_value}) does not meet the required criteria.')

            return func(*args, **kwargs)
        return inner
    return outer
