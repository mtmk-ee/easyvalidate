"""Module containing all classes used for validating
the types of single arguments.
"""

import abc
import collections.abc
import inspect
import logging
import typing


_LOGGER = logging.getLogger(__name__)
_EXEMPT_COLLECTION_TYPES = [str, bytes]


class _ArgumentValidator(abc.ABC):
    """ABC for validating arguments against a certain type.
    """

    def __init__(self, hint):
        """ABC for validating arguments against a certain type.

        Args:
            hint: the type hint for an argument. Can be a typing.______
                object, or a plain old class.
        """
        super().__init__()
        self._hint = hint
        self._origin = typing.get_origin(hint)
        self._hint_args = typing.get_args(hint)
        self._debug = False

        # Type hints may have arguments; store validators for these too
        self._sub_validators = [
            get_validator(hint)
            for hint in self._hint_args
        ]

    @property
    def type(self) -> type:
        """Gets the hint type. May be the origin or the hint passed to the
        constructor if the origin doesn't exist.
        """
        return self._origin or self._hint

    @property
    def sub_validators(self) -> typing.List['_ArgumentValidator']:
        """Generates a list of validators for nested type hints.
        May be empty if the type hint has no arguments.
        """
        return {
            x: x.sub_validators
            for x in self._sub_validators
        }

    @abc.abstractmethod
    def __str__(self) -> str:
        """String representation of the validator.
        Will only return a description of the type hint.
        """

    def __repr__(self) -> str:
        """Detailed string representation of the validator.
        Will return the type hint description, plus the name of
        the class.
        """
        return f'{str(self)} ({type(self).__name__})'

    @abc.abstractmethod
    def validate(self, arg, deep: bool):
        """Tests the argument against the type hint
        passed to the constructor of this class.

        Args:
            arg (Any): the object to test.
            deep (bool): whether to check each and every
                member of a collection, where applicable.
        """
        if self._debug:
            _LOGGER.debug(f'Testing {arg} against {str(self)}')


class _AnyValidator(_ArgumentValidator):
    """Validator for the `typing.Any` type hint.

    This type hint is super general, so testing it
    against anything will always result in success.
    """

    def __str__(self) -> str:
        return 'Any'

    def __repr__(self) -> str:
        return f'{str(self)} (Any)'

    def validate(self, arg, deep: bool):
        """Does nothing, really.

        Args:
            arg (Any): the object to test.
            deep (bool): unused.
        """
        return super().validate(arg, deep)


class _GenericValidator(_ArgumentValidator):
    """Validator for arguments where the type hint is a regular class.

    Doesn't support deep checking. If deep checking on a generic type is desired,
    a subclass should be made for it.
    """
    def __init__(self, hint):
        super().__init__(hint)

        # Safety check, since not all types can be used in validation.
        # "isinstance" won't normally raise unless something is really wrong.
        try:
            _ = isinstance(0, hint)
        except TypeError:
            raise TypeError(f'Type hint validation for "{self._hint}" is not supported')

    def __str__(self) -> str:
        return self._hint.__name__

    def __repr__(self) -> str:
        return f'{str(self)} (validated as generic)'

    def validate(self, arg, deep=False):
        """Tests the argument against the type hint
        passed to the constructor of this class.

        Args:
            arg (Any): the object to test.
            deep (bool): unused.

        Raises:
            TypeError if the argument is of the wrong type.
        """
        super().validate(arg, deep)
        if not isinstance(arg, self._hint):
            raise TypeError(
                f'Expected {str(self)} not ' f'{type(arg).__name__}'
            )


class _UnionValidator(_ArgumentValidator):
    """Validator for the `typing.Union` type hint.

    Always validates the members of the union, regardless
    of the `deep` flag.
    """

    def __str__(self) -> str:
        return ' | '.join(str(x) for x in self._sub_validators)

    def __repr__(self) -> str:
        return f'{str(self)} (validated as union)'

    def validate(self, arg, deep):
        """Tests the argument against the union type hint passed to the
        constructor of this class.

        Args:
            arg (Any): the object to test.
            deep (bool): whether to perform deep checking. This flag
                isn't used directly by this class, but is instead passed
                on to sub-validators.

        Raises:
            TypeError if the argument does not match _any_ members
            of the `Union` type hint.
        """
        super().validate(arg, deep)
        for validator in self._sub_validators:
            try:
                validator.validate(arg, deep)
                break
            except TypeError:
                continue
        else:
            raise TypeError(
                f'Expected {str(self)} not {_get_type_description(arg, deep)}'
            )


class _LiteralValidator(_ArgumentValidator):
    """Validator for the `typing.Literal` type hint.
    This class is used in the case that an auto-generated
    literal type hint appears in the function signature.
    """

    def __str__(self) -> str:
        return type(self._hint_args[0].__name__)

    def __repr__(self) -> str:
        return f'{str(self)} (validated as literal)'

    def validate(self, arg, deep=False):
        """Tests the argument against the literal type hint
        passed to the constructor of this class.

        Args:
            arg (Any): the object to test.
            deep (bool): unused.

        Raises:
            TypeError if the argument is not of the same type as
                the literal in the type hint.
        """
        super().validate(arg, deep)
        if not isinstance(arg, type(self._hint_args[0])):
            raise TypeError(
                f'Expected {str(self._sub_validators[0])} not '
                f'{_get_type_description(arg, deep)}'
            )


class _CollectionValidator(_ArgumentValidator):
    """Base class for validating collections.
    """

    def __init__(self, hint):
        super().__init__(hint)

    def __str__(self) -> str:
        sub_types = [str(x) for x in self._sub_validators]
        return (
            f'{(self._origin or self._hint).__name__}'
            + f'[{", ".join(sub_types)}]' if sub_types else ''
        )

    def __repr__(self) -> str:
        return f'{str(self)} (validated as collection)'

    @abc.abstractmethod
    def validate(self, arg, deep):
        """Tests the argument against the type hint passed to the
        constructor of this class.

        Args:
            arg (Any): the object to test.
            deep (bool): whether to perform deep checking on members
                of the collection.

        Raises:
            TypeError if the argument is of an invalid type.
        """
        super().validate(arg, deep)

        # Basic type checking needs to come before nested type checks
        if not isinstance(arg, self.type):
            raise TypeError(
                f'Expected {str(self)} not '
                f'{arg}'
            )


class _MappingValidator(_CollectionValidator):
    """Validator for Mapping-like collection type hints (e.g. dict)
    """

    def validate(self, arg, deep):
        """Tests the argument against the type hint passed to the
        constructor of this class.

        Args:
            arg (Any): the object to test.
            deep (bool): whether to perform deep checking. If true,
                all keys and values are deeply validated. Can be very
                slow on large collections.

        Raises:
            TypeError if the argument (or its children, if `deep=True`) are
                of invalid types.
        """
        super().validate(arg, deep)
        if self._hint_args and deep:
            for key, value in arg.items():
                try:
                    self._sub_validators[0].validate(key, deep)
                    self._sub_validators[1].validate(value, deep)
                except TypeError:
                    raise TypeError(
                        'Found invalid element in data. Expected'
                        f'"{str(self)}"'
                    )

class _SequenceValidator(_CollectionValidator):
    """Validator for Sequence-like collection type hints (e.g. tuple, list, set)
    """
    def __init__(self, hint):
        super().__init__(hint)
        self._exempt_collections = [str] # Members of a string are strings :(

    def validate(self, arg, deep):
        """Tests the argument against the type hint passed to the
        constructor of this class.

        Args:
            arg (Any): the object to test.
            deep (bool): whether to perform deep checking. If true,
                all values are deeply validated. Can be very
                slow on large collections.

        Raises:
            TypeError if the argument (or its children, if `deep=True`) are
                of invalid types.
        """
        super().validate(arg, deep)
        if self._hint_args and deep:
            validator = self._sub_validators[0]
            for elem in arg:
                try:
                    validator.validate(elem, deep)
                except TypeError:
                    raise TypeError(
                        'Found invalid element in data. Expected'
                        f'"{str(self)}"'
                        f' but got "{_get_type_description(elem, deep)}'
                    )


def _get_type_description(arg, deep=True) -> str:
    """Builds a string describing an instance's type.

    On collections, this function will recursively generate
    a list of all

    Args:
        arg: the instance.
        deep (bool): whether to recursively include, in the description,
            a list of all types present in the collection (where applicable).
            This can be pretty slow on large collections, use with caution.

    Returns:
        The string describing the instance's type.
    """
    if deep and isinstance(arg, collections.abc.Mapping):
        key_types, value_types = set(), set()
        for k, v in arg.items():
            key_types.add(k)
            value_types.add(v)
        key_types = ' | '.join(_get_type_description(x, deep) for x in key_types)
        value_types = ' | '.join(_get_type_description(x, deep) for x in value_types)
        return (
            f'{type(arg).__name__}' +
            f'[{key_types}, {value_types}]' if key_types else ''
        )
    elif deep and isinstance(arg, collections.abc.Sequence):
        if type(arg) in _EXEMPT_COLLECTION_TYPES:
            return type(arg).__name__

        types = {x for x in arg} # set, not a dict
        types = ' | '.join(_get_type_description(x, deep) for x in types)
        return (
            f'{type(arg).__name__}' +
            f'[{types}]' if types else ''
        )
    else:
        try:
            return type(arg).__name__
        except:
            return str(type(arg))


def get_validator(hint):
    """Factory function for fetching an appropriate validator
    for a particular type hint.

    Args:
        hint: the type hint that would appear in a function signature.

    Returns:
        The validator.
    """
    typing_validators = {
        typing.Any: _AnyValidator,
        typing.Union: _UnionValidator,
        typing.Literal: _LiteralValidator,
    }
    collection_validators = {
        collections.abc.Mapping: _MappingValidator,
        collections.abc.Sequence: _SequenceValidator,
    }

    origin = typing.get_origin(hint)
    validator = typing_validators.get(origin or hint, None)
    if validator:
        return validator(hint)

    for t, validator in collection_validators.items():
        if hint in _EXEMPT_COLLECTION_TYPES:
            continue
        elif origin and issubclass(origin, t):
            return validator(hint)
        elif inspect.isclass(origin or hint) and issubclass(origin or hint, t):
            return validator(hint)

    return _GenericValidator(hint)
