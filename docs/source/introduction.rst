Introduction
===============


Installation
------------

Install the package into your environment:

.. code-block:: console

   $ pip install easyvalidate


Type Hint Validation
--------------------

Type validation for arguments passed to functions can be done
using the :py:func:`~easyvalidate.validate_typehints` decorator.

Simply define your function with argument type hints and the
decorator will do the rest

.. doctest::

   >>> from easyvalidate import validate_typehints
   >>> from typing import Union
   >>>
   >>> @validate_typehints()
   ... def increment(x: Union[int, float]):
   ...   return x + 1
   >>>
   >>> increment(1)
   2
   >>> increment('not valid!')
   Traceback (most recent call last):
      ...
   TypeError: Invalid type supplied for argument "x": Expected int | float not str


.. warning::

   This decorator does not yet support Python 3.10 style unions.
