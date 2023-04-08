import functools
from functools import cached_property
import inspect
import types

from easyvalidate._helpers import is_function


class FunctionInfo:

    def __init__(self, func) -> None:
        if not is_function(func):
            raise TypeError('Argument must be a function')
        self._func = func

    @property
    def func(self):
        return self._func

    @property
    def name(self):
        return self._func.__name__

    @cached_property
    def is_method(self) -> bool:
        if inspect.ismethod(self._func):
            return True

    @cached_property
    def unwrapped(self):
        return inspect.unwrap(self._func)

    @cached_property
    def module(self):
        return inspect.getmodule(self._func)
