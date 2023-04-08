"""Module for generating expression trees from a value placeholder.
These expressions are "lazy-evaluated," meaning you can store the
expressions and evaluate them at any time.

The main use of this is for expression validation.

Examples:

```
>>> expr = X + 10
>>> expr.substitute(2)
12

>>> expr = (X / 100) < 10
>>> expr.substitute(1000)
False
```
"""
from easyvalidate.exceptions import ExpressionError

#################### Operator ####################
_operators = [
    # Comparison
    'eq',
    'ne',
    'gt',
    'ge',
    'lt',
    'le',

    # Bitwise
    'and',
    'rand',
    'or',
    'ror',
    'xor',
    'rxor',
    'not',
    'lshift',
    'rlshift',
    'rshift',
    'rrshift',

    # Arithmetic
    'add',
    'radd',
    'sub',
    'rsub',
    'mul',
    'rmul',
    'truediv',
    'rtruediv',
    'floordiv',
    'rfloordiv',
    'mod',
    'rmod',
    'pow',
    'rpow',

    # Misc
    'call',
]
# Some operators are impossible to lazy-evaluate
_unsupported_operators = {
    'len': 'Use of len() in test expression is unsupported.',
    'contains': 'Use of "in" keyword" in test expression is unsupported.'
}


def _make_operator(dunder: str):
    """Returns an operator function that returns an
    expression node for lazy evaluation.

    Args:
        dunder (str): the operator dunder name.
    """
    def operator(*args, **kwargs):
        return _ExpressionNode(dunder, *args, **kwargs)
    return operator


def _make_unsupported_operator(reason: str):
    """Returns a function that will raise a TypeError
    with the given description.

    Args:
        reason (str): the reason the TypeError is raised.
    """
    def operator(*args, **kwargs):
        raise ExpressionError(reason)
    return operator


class _OperatorAbsorber:
    """Special class for absorbs (most) operators used on it
    (e.g. +, -, *, ()), and creates expression nodes for
    lazy evaluation instead.
    """
    def __getattr__(self, name: str):
        """Special implementation for get_attr, used
        for attribute lookup of a placeholder.

        Args:
            name (str): the name of the attribute

        Returns:
            A `_GetAttrExpressionNode` that can be used
            to fetch an attribute from a placeholder.
        """
        return _GetAttrExpressionNode(name, self)


def _populate_operators():
    """Populates the `_OperatorAbsorber` class with all
    the supported/unsupported operators.

    Easier to do this after the class has been defined
    since the vast majority of operators are identical.
    """
    for op_name in _operators:
        op_name = f'__{op_name}__'
        op_fn = _make_operator(op_name)
        setattr(_OperatorAbsorber, op_name, op_fn)

    for op_name, reason in _unsupported_operators.items():
        op_fn = _make_unsupported_operator(reason)
        setattr(_OperatorAbsorber, f'__{op_name}__', op_fn)

_populate_operators() # Keeps variables out of global namespace


#################### Expression ####################
class _ExpressionNode(_OperatorAbsorber):
    """Represents a node in an expression tree.

    Instances of this class are also operator absorbers,
    meaning the tree builds itself when using operators on
    instances.
    """

    def __init__(self, attr: str, *args, **kwargs) -> None:
        """Creates a new expression node.

        Args:
            attr (str): the name of the function ("evaluator") belonging
                to a placeholder, called to
                evaluate the node
            *args, **kwargs: the arguments to pass to the evaluator. These
                values can be placeholders.
        """
        self._attr = attr
        self._args = args
        self._kwargs = kwargs

    def substitute(self, placeholder_value):
        """Evaluates this expression node recursively
        using a value for any placeholders.

        Args:
            placeholder_value (Any): the value to substitute for
                placeholders.

        Returns:
            The result of the operation.
        """
        args = [
            self._substitute_arg(x, placeholder_value)
            for x in self._args
        ]
        kwargs = {
            k: self._substitute_arg(v, placeholder_value)
            for k, v in self._kwargs.items()
        }
        op = getattr(args[0], self._attr)
        return op(*args[1:], **kwargs)

    def _substitute_arg(self, arg, placeholder_value):
        """Determines the substituted value of an argument.

        If the argument is a placeholder, it is directly substituted.
        If the argument is another expression, it is evaluated.
        If the argument is neither (a constant), it is returned.

        Args:
            arg (Any): the argument.
            placeholder_value (Any): the value to substitute.

        Returns:
            The evaluated argument.
        """
        if is_expression(arg):
            return arg.substitute(placeholder_value)
        return arg


class _GetAttrExpressionNode(_ExpressionNode):
    """Special expression node for getting attributes.
    """

    def __init__(self, attr: str, object) -> None:
        """Create an expression node for getting attributes from
        a placeholder or other object.

        Args:
            attr (str): the attribute name.
            object (Any): the object to retrieve the attribute from.
                This can be a placeholder.
        """
        super().__init__(attr)
        self._object = object

    def substitute(self, placeholder_value):
        """Substitutes any placeholders for real values, and returns
        an attribute fetched from the result.

        Args:
            placeholder_value (Any): the value to substitute.

        Returns:
            The attribute.
        """
        object = self._substitute_arg(self._object, placeholder_value)
        return getattr(object, self._attr)


#################### Placeholder ####################
class _PlaceholderMeta(type, _OperatorAbsorber):
    """Metaclass for the placeholder class. Allows
    lazy-evaluatable expressions to be generated from operations
    applied to a class, rather than an object.
    """
    # An explicit definition for __call__ is necessary since "type" overrides it.
    __call__ = _OperatorAbsorber.__call__


class _Placeholder(metaclass=_PlaceholderMeta):
    """Represents a placeholder value. Generates expression trees
    that can be evaluated at any time with a real value.
    """

    def substitute(placeholder):
        """Implements the identity substitution.
        Takes no "self" argument since the placeholder class cannot
        be instantiated.

        Doesn't inherit `_ExpressionNode` since that class must be
        instantiated.

        Args:
            placeholder (Any): the value to substitute.
        """
        return placeholder


class X(_Placeholder):
    """Represents a placeholder value. Generates expression trees
    that can be evaluated at any time with a real value.

    Useful for more complicated function argument validations,
    since an argument can be tested against an expression.

    The use of the placeholder does have limitations in what kinds
    of expressions can be used:
    - the `in` keyword cannot be used.
    - the `len()` function cannot be used.
    - the placeholder cannot be passed to functions.
    - ___ < X < ___ cannot be used.
    - boolean operators `and`, `or`, and `not` cannot be used.
    """


def is_placeholder(value):
    """Checks if the given value is a placeholder.

    Args:
        value (Any): the value to test.

    Returns:
        True if the value is a placeholder
    """
    try:
        return issubclass(value, _Placeholder)
    except:
        return False


def is_expression(value):
    """Checks if the given value is an expression.

    Args:
        value (Any): the value to test.

    Returns:
        True if the value is an expression.
    """
    is_node = issubclass(type(value), _ExpressionNode)
    return is_node or is_placeholder(value)
