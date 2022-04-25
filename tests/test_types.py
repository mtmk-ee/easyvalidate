from typing import Any, List, Dict, Tuple, Union

import pytest

from easyvalidate import validate_typehints


def test_deep_flag():

    def case1(x: List[List[int]]):
        return True

    def case2(x: Dict[Union[int, str], List[Union[int, str]]]):
        return True

    func = validate_typehints(deep=False)(case1)
    assert func([]) is True
    assert func([10]) is True
    assert func(['str']) is True
    call_raises(TypeError, func, {})

    func = validate_typehints(deep=True)(case1)
    assert func([]) is True
    assert func([[], [], []]) is True
    assert func([[10, 20], [10, 20]]) is True
    call_raises(TypeError, func, [[10, 20], [10, 20, str]])

    func = validate_typehints(deep=True)(case2)
    assert func({}) is True
    assert func({10: []}) is True
    assert func({10: [10, 'test']}) is True
    assert func({'test': [10, 'test']}) is True
    call_raises(TypeError, func, str)
    call_raises(TypeError, func, {bytes: []})
    call_raises(TypeError, func, {10: str})
    call_raises(TypeError, func, {10: [bytes]})
    call_raises(TypeError, func, {10: [[]]})


def test_simple_types():

    def case1(x: int):
        return True

    def case2(x: int, y: dict):
        return True

    # fn(x: int)
    func = validate_typehints()(case1)
    assert func(0)
    assert func(x=0)
    call_raises(TypeError, func, 0.1)
    call_raises(TypeError, func, [])
    call_raises(TypeError, func, type)

    # fn(x: int, y: dict)
    func = validate_typehints()(case2)
    assert func(0, {})
    assert func(0, y={})
    assert func(x=0, y={})
    assert func(y={}, x=0)
    call_raises(TypeError, func, {}, 0)
    call_raises(TypeError, func, x={}, y=0)
    call_raises(TypeError, func, '', {})
    call_raises(TypeError, func, 0, '')


def test_union_hint():
    def case1(x: Union[int, float]):
        return True

    # fn(x: int | float)
    func = validate_typehints()(case1)
    assert func(0)
    assert func(x=0)
    assert func(2.718)
    assert func(x=2.718)
    call_raises(TypeError, func, [])
    call_raises(TypeError, func, type)


def test_any_hint():
    def case1(x: Any):
        return True

    def case2(x: int, y: Any):
        return True

    # fn(x: Any)
    func = validate_typehints()(case1)
    assert func(0)
    assert func('some value')
    assert func(type)

    # fn(x: int, y: Any)
    func = validate_typehints()(case2)
    assert func(0, 0) is True
    assert func(0, None) is True
    assert func(0, 'hello') is True
    call_raises(TypeError, func, 'bad arg', 1337)


def test_variadic_args():

    def variadic_args(*args, **kwargs):
        pass

    with pytest.raises(NotImplementedError):
        validate_typehints()(variadic_args)


def test_return_hint():

    @validate_typehints()
    def test(x: int) -> bool:
        return True

    assert test(0) is True


def test_missing_hints():

    def case1(x, y: int):
        return True

    func = validate_typehints(all=False)(case1)
    assert func('hi', 0) is True

    with pytest.raises(TypeError):
        validate_typehints(all=True)(case1)



def test_methods():

    class TestClass:

        @validate_typehints()
        def method(self, x: int):
            return True

        @classmethod
        @validate_typehints()
        def class_method(cls, x: int):
            return True

        @staticmethod
        @validate_typehints()
        def static_method(x: int):
            return True

    instance = TestClass()
    assert instance.method(0) is True
    call_raises(TypeError, instance.method, [])

    assert TestClass.class_method(0) is True
    call_raises(TypeError, TestClass.class_method, [])

    assert TestClass.static_method(0) is True
    call_raises(TypeError, TestClass.static_method, [])


def call_raises(err_type, func, *args, **kwargs):
    with pytest.raises(err_type):
        func(*args, **kwargs)

