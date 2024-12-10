from random import randint
from typing import Callable, TypeVar
from unittest import TestCase

from utils.test import note
from . import Monoid

T = TypeVar("T")


def generate_monoid_test(monoid_class: type[Monoid[int]]):
    Monoid = monoid_class

    class TestMonoid(TestCase):
        @note(f"{monoid_class} 연결성 테스트")
        @note(f"{monoid_class}는 이항연산이 가능해야됨")
        def test_monoid_has_connectivity(self):
            x = Monoid.of(5)
            y = Monoid.of(10)
            z = Monoid.combined(x, y, lambda x, y: x * y)
            self.assertEqual(z.value, 50)

        @note(f"{monoid_class} 항등원 테스트")
        @note(
            f"메이비는 특정한 값 x가 있어 임의의 y에 대해 x*y == y*x = y를 만족해야됨"
        )
        def test_monoid_has_identity(self):
            certain = Monoid.identity()
            random = Monoid.of(randint(1, 100))
            a = Monoid.combined(certain, random, lambda x, y: x - y)
            b = Monoid.combined(random, certain, lambda x, y: x - y)
            self.assertEqual(a, b)
            a = Monoid.combined(certain, random, lambda x, y: x * y)
            b = Monoid.combined(random, certain, lambda x, y: x * y)
            self.assertEqual(a, b)

        @note(f"{monoid_class} 결합법칙 테스트")
        @note(f"{monoid_class}는 x,y,z에 대해 (x*y)*z == x*(y*z)가 성립함")
        def test_monoid_has_association(self):
            x, y, z = Monoid.of(2), Monoid.of(3), Monoid.of(6)
            multiplier: Callable[[int, int], int] = lambda x, y: x * y
            left = x.combined(y, multiplier).combined(z, multiplier)
            right = x.combined(y.combined(z, multiplier), multiplier)
            self.assertEqual(left, right)

    return TestMonoid
