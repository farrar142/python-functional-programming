from functools import wraps
from typing import Callable, ParamSpec, TypeVar
from unittest import TestCase, main

from utils.test import note

from .maybe import Maybe


class TestMaybe(TestCase):
    @note("메이비 생성 테스트")
    def test_1(self):
        maybe = Maybe.of(5)
        self.assertIsInstance(maybe, Maybe)

    @note("메이비 초기값 테스트")
    def test_2(self):
        maybe = Maybe.of(5)
        self.assertEqual(maybe.get(), 5)

    @note("메이비에 콜러블을 할당 할 수 있어야함")
    def test_3(self):
        maybe = Maybe.call(lambda: 5)
        self.assertEqual(maybe.get(), 5)

    @note("메이비는 map을 통해 새로운 메이비를 반환해야됨")
    def test_4(self):
        maybe = Maybe.of(5).map(lambda x: str(x))
        self.assertIsInstance(maybe, Maybe)
        self.assertEqual(maybe.get(), "5")

    @note("메이비의 map은 체이닝이 되어야됨")
    def test_5(self):
        maybe = Maybe.of(5).map(lambda x: str(x)).map(int)
        self.assertEqual(maybe.get(), 5)

    @note("메이비의 플랫맵은 옵셔널리턴값을 평탄화해야됨")
    def test_5_2(self):
        maybe = Maybe.of(5).map(lambda x: Maybe.of(5))
        self.assertIsInstance(maybe.get(), Maybe)
        maybe = Maybe.of(5).flat_map(lambda x: Maybe.of(5)).map(int)
        self.assertEqual(maybe.get(), 5)

    @note("메이비는 값 혹은 None을 반환해야됨")
    def test_6(self):
        maybe = Maybe.of(5)
        self.assertEqual(maybe.get(), 5)

    @note("메이비는 value에 값을 접근 할 수 없어야됨")
    def test_7(self):
        maybe = Maybe.of(5)
        with self.assertRaises(Exception):
            maybe.value  # type:ignore

    @note("메이비의 orElse로 값이 None일시 대체 값을 반환해야됨")
    def test_8(self):
        maybe = Maybe[int].empty(None)
        self.assertEqual(maybe.orElse(5), 5)

    @note("메이비의 orElse에 함수값이 필요 할 시 orElseGet을 사용해야됨")
    def test_9(self):
        maybe = Maybe[int].empty(None)
        self.assertEqual(maybe.orElseGet(lambda: 5), 5)

    @note("메이비의 orElseGet은 값이 있을 경우엔 실행되면 안됨")
    def test_10(self):
        maybe = Maybe[int].of(5)

        def get_func():
            raise Exception

        self.assertEqual(maybe.orElseGet(get_func), 5)

    @note("메이비의 orElseGet은 값이 없을 경우엔 실행되어야됨")
    def test_11(self):
        maybe = Maybe[int].empty(None)

        def get_func():
            raise Exception

        with self.assertRaises(Exception):
            maybe.orElseGet(get_func)

    @note("메이비에 값이 없을 경우에 error를 반환하는 메서드가 orElseThrow가 있어야됨")
    def test_12(self):
        maybe = Maybe[int].empty(None)
        with self.assertRaises(ZeroDivisionError):
            maybe.orElseThrow(ZeroDivisionError)

    @note("메이비에 값이 있을 경우에 orElseThrow는 에러를 반환하면 안됨")
    def test_13(self):
        maybe = Maybe.of(5)
        self.assertEqual(maybe.orElseThrow(Exception), 5)

    @note("메이비의 orElseThrow는 Exception 인스턴스도 받아야됨")
    def test_14(self):
        maybe = Maybe[int].empty(None)
        with self.assertRaises(ZeroDivisionError):
            maybe.orElseThrow(ZeroDivisionError("인스턴스"))

    @note("메이비의 wraps는 함수를 데코레이션 해야됨")
    def test_15(self):
        @Maybe.wraps
        def wrapped(a: int, b: int) -> int | None:
            return a + b

        maybe = wrapped(1, 2)
        self.assertEqual(maybe.get(), 3)

    @note("메이비 LightIdentity테스트 Maybe(x).chain(f) == f(x) ")
    def test_16(self):
        @Maybe.wraps
        def square(a: int):
            return a * a

        left = Maybe.of(5).flat_map(square)
        right = square(5)
        self.assertEqual(left.orElseThrow(), 25)
        self.assertEqual(right.orElseThrow(), 25)
        self.assertEqual(left, right)

    @note("메이비 RightIdentity테스트 Maybe.of(5).chain(Maybe.of) === Maybe(5)")
    def test_17(self):

        left = Maybe.of(5).flat_map(Maybe.of)
        right = Maybe.of(5)
        self.assertEqual(left, right)

    @note(
        "메이비 결합법칙 테스트 Maybe(x).chain(f).chain(g) == Maybe(x).chain(x=>f(x).chain(g))가 성립해야된다"
    )
    def test_18(self):
        @Maybe.wraps
        def square(a: int):
            return a * a

        @Maybe.wraps
        def stringify(a: int):
            return str(a)

        left = Maybe.of(5).flat_map(square).flat_map(stringify)
        right = Maybe.of(5).flat_map(lambda x: square(x).flat_map(stringify))
        self.assertEqual(left.orElseThrow(), "25")
        self.assertEqual(right.orElseThrow(), "25")
        self.assertEqual(left, right)
