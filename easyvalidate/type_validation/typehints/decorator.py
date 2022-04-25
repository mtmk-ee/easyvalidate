import inspect
import logging
import functools

from .function_validator import FunctionValidator, MethodValidator


_LOGGER = logging.getLogger('naluvalidation.validate_types')


def validate_typehints(all=True, deep=False, clean_trace=True):
    """Decorator for enforcing types of function arguments
    based on type hints.

    Args:
        all (bool): whether to ensure all arguments have type hints
        deep (bool): whether to check nested type hints
        clean_trace (bool): whether to clean the stack trace when
            errors occur. Type checking can blow up the stack, so
            only turn this flag off if you're debugging the validator
            itself.

    Raises:
        TypeError if type hints are missing when `all=True`, or if
        one or more type hints are unsupported.
    """
    def wrapper(func):
        argspec = inspect.getfullargspec(inspect.unwrap(func))
        if argspec.varargs or argspec.varkw:
            raise NotImplementedError('Variadic arguments not supported')

        arg_names = argspec.args
        if arg_names and arg_names[0] in ['self', 'cls']:
            enforcer = MethodValidator(func, all, deep)
        else:
            enforcer = FunctionValidator(func, all, deep)

        @functools.wraps(func)
        def inner(*args, **kwargs):
            try:
                enforcer.validate(*args, **kwargs)
            except TypeError as e:
                _LOGGER.error(f'Type validation failed on function {func.__name__}: {e}')
                if clean_trace:
                    raise e from None
                else:
                    raise e

            return func(*args, **kwargs)
        return inner
    return wrapper
