API
***


Decorators
==========

EasyValidate provides several decorators for validating function arguments
before they ever reach the body of the function. In general, this looks
like

.. code-block:: python

    @the_decorator(opt1, opt2, ...)
    def my_function(arg1, arg2, ...):
        # use arguments safely here


Type Hints
----------

The type hint validation decorator analyzes the type hints for the
function it is applied to. When the function is called, the decorator
ensures the argument types match those specified in the type hints
-- otherwise, it raises an error before reaching the body of the function.

.. autofunction:: easyvalidate.validate_typehints
