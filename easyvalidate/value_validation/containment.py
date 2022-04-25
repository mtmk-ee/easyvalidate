import functools

from easyvalidate._helpers import get_argument_dict, get_argument_names


def validate_containment(**collections):
    """Decorator for making sure that values passed to a function are
    contained within a given collection.

    Takes keyword arguments of `ARG_NAME=COLLECTION`.

    Raises:
        NameError if one or more arguments specified do not exist in the function
            signature.
        TypeError if a collection specified does not support the "in" operator.
    """
    def outer(func):
        arg_names = get_argument_names(func)
        for arg_name, collection in collections.items():
            if arg_name not in arg_names:
                raise NameError(f'Cannot specify allowed values for non-existent argument "{arg_name}".')
            elif not hasattr(collection, '__contains__'):
                raise TypeError(f'Type for argument "{arg_name}" does not allow containment validation.')

        @functools.wraps(func)
        def inner(*args, **kwargs):
            all_args = get_argument_dict(arg_names, args, kwargs)

            for arg_name, collection in collections.items():
                given_value = all_args[arg_name]
                if given_value not in collection:
                    raise ValueError(f'Value for "{arg_name}" is not found among the allowed values: {collection}')

            return func(*args, **kwargs)
        return inner
    return outer
