import inspect
import itertools
from typing import List


def get_argument_names(func) -> List[str]:
    """Gets the argument names of a function, ignoring any
    decorators that might wrap the function.

    Args:
        func: the function

    Returns:
        A list of argument names.
    """
    return inspect.getfullargspec(inspect.unwrap(func)).args


def get_argument_dict(arg_names: List[str], args: tuple, kwargs: dict):
    """Converts *args and **kwargs to a dictionary of named arguments.

    Args:
        arg_names (List[str]): the list of argument names of a function.
        args (tuple): the positional arguments
        kwargs (dict): the keyword arguments

    Returns:
        A dictionary of {arg_name: arg_value}
    """
    named_args = [(arg_names[i], arg) for i, arg in enumerate(args)]
    return dict(itertools.chain(named_args, kwargs.items()))
