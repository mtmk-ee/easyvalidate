[![Documentation Status](https://readthedocs.org/projects/easyvalidate/badge/?version=latest)](https://easyvalidate.readthedocs.io/en/latest)

# easyvalidate

A Python package containing utilities for different types of validations:

- Validation of types
- Validation of values based on various conditions
- Validation of method protection


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


### Caller Validation
Sometimes we _really_ don't want people calling internal methods (i.e. those that start with an underscore by convention)
from outside the enclosing class. Here we can use the `@private` or `@protected` decorators:

```py
from easyvalidate import private, protected

class Foo:
    @protected
    def _my_protected_meth(self):
        pass

    @private
    def _my_private_meth(self):
        pass

    def my_public_meth(self):
        self._my_protected_meth() # works as expected
        self._my_private_meth() # works as expected

class Bar(Foo):

    def my_public_meth(self):
        self._my_protected_meth() # works as expected
        self._my_private_func() # error!
```

The `@private` and `@public` decorators are a bit limited as of now:
- They only work for CPython for now.
- They don't prevent overriding the methods in subclasses.
