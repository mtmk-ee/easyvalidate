import operator
from decimal import Decimal

import pytest

from easyvalidate import X
from easyvalidate.value_validation.lazy_evaluation import (
    is_expression,
    is_placeholder,
)
from easyvalidate.exceptions import ExpressionError


def test_comparison():
    """Test comparison operators.
    """
    expr = X == 5
    assert subs(expr, 5) is True
    assert subs(expr, 2) is False

    expr = X != 5
    assert subs(expr, 10) is True
    assert subs(expr, 5) is False

    expr = X < 5
    assert subs(expr, 10) is False
    assert subs(expr, 2) is True

    expr = X > 5
    assert subs(expr, 10) is True
    assert subs(expr, 2) is False

    expr = X <= 5
    assert subs(expr, 5) is True
    assert subs(expr, 10) is False

    expr = X >= 5
    assert subs(expr, 5) is True
    assert subs(expr, 2) is False


def test_arithmetic(arithmetic_operators):
    """Test arithmetic operators.
    """
    operators = arithmetic_operators
    operands = [Decimal(x) for x in range(-10, 10)]
    checks = [
        (left, op, right)
        for op in arithmetic_operators.keys()
        for left in operands
        for right in operands
        if not (right == 0 and op in ['/', '//', '%']) and \
            not (left == right == 0 and op in ['**'])
    ]
    check_handed_operators(checks, operators)


def test_bitwise(bitwise_operators):
    operators = bitwise_operators
    operands = range(-10, 10)
    checks = [
        (left, op, right)
        for op in operators.keys()
        for left in operands
        for right in operands
        if not (right < 0 and op in ['<<', '>>'])
    ]
    check_handed_operators(checks, operators)


def test_invalid_operations():
    """Test operations that don't work
    """
    with pytest.raises(ExpressionError):
        len(X)

    with pytest.raises(ExpressionError):
        5 in X, [5, 10]

    with pytest.raises(ExpressionError):
        0 < X < 5

    dummy = 5
    with pytest.raises(ExpressionError):
        X and dummy
    with pytest.raises(ExpressionError):
        X or dummy
    with pytest.raises(ExpressionError):
        not X

    with pytest.raises(ExpressionError):
        bool(X)


def test_nested_expressions():
    """Test evaluating nested expressions.
    """
    expr = (X + 5) * X
    assert subs(expr, 2) == 14

    expr = (X + 5) * 3
    assert subs((X + 5) * X, 2) == 14

    expr = (X + 5) * 3 - 2 + 2 * X % 5
    assert subs(expr, 2) == 23


def test_getattr():
    """Test getting attributes from objects.
    """
    class Dummy:
        some_value = 10
        def some_function(self, x, y):
            return x + y

        class Dummy2:
            some_other_value = 20
        dummy2 = Dummy2()

    dummy = Dummy()
    assert subs(X.some_value * 2, dummy) == 20
    assert subs(X.some_function(1 + X.some_value, 2), dummy) == 13
    assert subs(X.dummy2.some_other_value * 2, dummy) == 40


def test_callable():
    """Test substituting functions.
    """
    def func(x, y):
        return x + y

    assert subs(X(1, 2), func) == 3

    class SomeClass:
        def method(self, x, y):
            return x + y

    assert subs(X(1, 2), SomeClass().method) == 3


def test_is_placeholder():
    """Test the `is_placeholder` function.
    """
    assert is_placeholder(X) is True
    assert is_placeholder(X + 5) is False
    assert is_placeholder(5) is False

def test_is_expression():
    """Test the `is_expression` function.
    """
    assert is_expression(X) is True
    assert is_expression(X + 5) is True
    assert is_expression(5) is False


def subs(expr, x):
    """Substitutes a value into an expression.
    Ensures that the expression really is an expression.

    Args:
        expr: the expression
        x: the value to substitute

    Returns:
        The result
    """
    assert is_expression(expr)
    return expr.substitute(x)


def check_handed_operators(checks, operators):
    """Tests several handed (left/right) operators.

    Args:
        checks (List[tuple]): A list of (left value, operator name, right value) checks.
        operators (dict): dict of operators {op name: op func}
    """
    for left, op_name, right in checks:
        try:
            op_fn = operators[op_name]
            expected = op_fn(left, right)
            assert subs(op_fn(X, right), left) == expected
            assert subs(op_fn(left, X), right) == expected
        except AssertionError as e:
            raise AssertionError(f'Operation {left} {op_name} {right} failed: {e}')


@pytest.fixture
def arithmetic_operators():
    return {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '//': operator.floordiv,
        '**': operator.pow,
        '%': operator.mod,
    }

@pytest.fixture
def bitwise_operators():
    return {
        '<<': operator.lshift,
        '>>': operator.rshift,
        '&': operator.and_,
        '|': operator.or_,
        '^': operator.xor,
    }
