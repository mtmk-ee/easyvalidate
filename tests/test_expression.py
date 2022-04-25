from easyvalidate import X, validate_expression
from easyvalidate.exceptions import ExpressionError

import pytest



def test_valid_expression():
    """Test decorator expressions that should work.
    """

    @validate_expression(x=(X < 10))
    def some_function(x):
        pass

    some_function(2)

    with pytest.raises(ValueError):
        some_function(20)


def test_invalid_expression():
    """Test decorator expressions that shouldn't work.
    """

    with pytest.raises(TypeError):
        @validate_expression(x=10)
        def func(x):
            pass

    with pytest.raises(ExpressionError):
        @validate_expression(x=len(X) < 10)
        def func(x):
            pass

    with pytest.raises(ExpressionError):
        @validate_expression(x=5 in X)
        def func(x):
            pass

    with pytest.raises(NameError):
        @validate_expression(y=X)
        def func(x):
            pass
