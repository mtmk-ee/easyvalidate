import inspect
from typing import List

from .arguments import get_argument_dict, get_argument_names


def is_function(obj):
    return callable(obj) and not inspect.isclass(obj)



