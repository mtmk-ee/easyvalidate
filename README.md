[![Documentation Status](https://readthedocs.org/projects/easyvalidate/badge/?version=latest)](https://easyvalidate.readthedocs.io/en/latest)

# easyvalidate

A Python package containing utilities for different types of validations:

- Validation of types
- Validation of values based on various conditions


## Installation

You can install the package from PyPI using pip:

```
$ pip install easyvalidate
```

## Feature Highlights

### Typehint Validation
The package contains a decorator: `validate_types()`. Add it to any
function you want to validate types for, but make sure you have type hints
on your function:

```py
import typing

from easyvalidate import validate_typehints

@validate_typehints()
def foo(x: int, y: typing.Union[int, str]):
    print(x, y)

foo(5, 10) # works
foo(5, 'hello!') # also works
foo(5, []) # error!
```

The decorator comes with a few arguments:
- `all: bool = True`: whether to require that all arguments (except `self`) are type-hinted. It's enabled by default.
- `deep: bool = False`: whether to recursively validate all members of collections passed to the function. This can be painfully slow on large datasets so it's disabled by default.
