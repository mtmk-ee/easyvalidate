import typing

from easyvalidate._helpers import get_argument_dict, get_argument_names
from .arg_validators import get_validator


_NoType = object()


class FunctionValidator:
    """Class for function argument type validation.

    After creating the class, use the `validate()` function to test
    several arguments against the type hints that the previously-given
    function specifies.
    """

    def __init__(self, func, all: bool=True, deep: bool=False):
        """Class for function argument type validation.

        Args:
            instance (object): instance of the class which func is bound to (can be None)
            func (callable): the function to wrap
            all (bool): whether to ensure all arguments have type hints
            deep (bool): whether to check nested type hints

        Raises:
            TypeError if type hints are missing when `all=True`, or if
            one or more type hints are unsupported.
        """
        self._all = all
        self._deep = deep
        self._func = func
        self._arg_names, self._type_hints = self._get_arg_details(func)

        self._validators = {
            name: get_validator(hint)
            for name, hint in self._type_hints.items()
        }

    def _get_arg_details(self, func) -> typing.Tuple[list, dict]:
        """Fetches details about the function arguments and their
        typehints.

        Args:
            func: the function to inspect

        Returns:
            A tuple of (argument name list, {argument name: type hint}).
            The sizes of each may or may not be equal, depending on
            whether the `all` flag is set.

        Raises:
            TypeError if the `all` flag is set, and there are one or more
            type hints missing from the function signature.
        """
        arg_names = get_argument_names(func)
        type_hints = typing.get_type_hints(func)
        if 'return' in type_hints:
            del type_hints['return']

        # Need to make sure all arguments that should have type hints do have type hints
        if self._all and len(arg_names) != len(type_hints):
            raise TypeError('One or more type hints is missing from the function definition')

        return arg_names, type_hints

    def validate(self, *args, **kwargs):
        """Validates position/keyword arguments against the type hints
        specified in the function signature. If validated successfully,
        this function will be quiet.

        Raises:
            TypeError if at least one argument has the wrong type.
        """
        all_args = get_argument_dict(self._arg_names, args, kwargs)
        for name, arg in all_args.items():
            type_hint = self._type_hints.get(name, _NoType)
            if type_hint == _NoType:
                continue

            try:
                self._validators[name].validate(arg, self._deep)
            except TypeError as e:
                raise TypeError(
                    f'Invalid type supplied for argument "{name}": {e}'
                )

    def get_validators(self) -> dict:
        """Gets the internal list mapping of validators used to
        validate each argument.

        Returns:
            A dict of {arg_name: validator}.
        """
        return {
            name: validator.sub_validators
            for name, validator in self._validators.items()
        }


class MethodValidator(FunctionValidator):
    """Class for method argument type validation.

    After creating the class, use the `validate()` function to test
    several arguments against the type hints that the previously-given
    method specifies.

    There is no validation done on the "self" argument.
    """

    def _get_arg_details(self, func) -> typing.Tuple[list, dict]:
        """Fetches details about the function arguments and their
        typehints.

        Args:
            func: the function to inspect

        Returns:
            A tuple of (argument name list, {argument name: type hint}).
            The sizes of each may or may not be equal, depending on
            whether the `all` flag is set.

        Raises:
            TypeError if the `all` flag is set, and there are one or more
            type hints missing from the function signature.
        """
        arg_names = get_argument_names(func)[1:] # strip out "self" or "cls" arg
        type_hints = typing.get_type_hints(func)
        if 'return' in type_hints:
            del type_hints['return']

        # Need to make sure all arguments that should have type hints do have type hints
        if self._all and len(arg_names) != len(type_hints):
            raise TypeError('One or more type hints is missing from the function definition')

        return arg_names, type_hints

    def validate(self, *args, **kwargs):
        """Validates position/keyword arguments against the type hints
        specified in the method signature. If validated successfully,
        this function will be quiet.

        Ignores the first positional argument "self".

        Raises:
            TypeError if at least one argument has the wrong type.
        """
        super().validate(*args[1:], **kwargs)
