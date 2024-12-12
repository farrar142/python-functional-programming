from random import randint
from typing import Callable
from unittest import TestCase

from delay.delay import Delay
from monoid.test import generate_monoid_test
from utils.test import note


class Container:
    def __init__(self, value: int):
        self.value = value

    def power(self):
        self.value = self.value * self.value
        return self


class TestDelay(TestCase):
    @note("딜레이는 함수를 감싸고, 최종 호출을 해야지 실행이됨")
    def test_1(self):
        @Delay
        def test(container: Container):
            container.value += 1

        container = Container(0)
        delayed = test(container)
        self.assertEqual(container.value, 0)
        delayed.run()
        self.assertEqual(container.value, 1)

    @note("딜레이끼리는 bind가 가능해야됨")
    def test_2(self):
        @Delay
        def increase(container: Container):
            container.value += 1
            return container

        def power(container: Container):
            def inner():
                container.value = container.value * container.value
                return container

            return Delay(inner)

        @Delay
        def test(container: Container):
            return container.value + 2

        container = Container(1)
        delay = increase(container).bind(power)
        self.assertEqual(container.value, 1)
        delay.run()
        self.assertEqual(container.value, 4)
        delay2 = increase.bind(power)
        self.assertEqual(container.value, 4)
        delay2.run(container)
        self.assertEqual(container.value, 25)
        container = Container(5)
        two = increase(container).bind(power).bind(increase)
        self.assertEqual(container.value, 5)
        two.run()
        self.assertEqual(container.value, 37)

        container = Container(3)
        three = power(container).bind(power).bind(test)
        self.assertEqual(container.value, 3)
        self.assertEqual(three.run(), 83)
        print(three)
        # increase.bind(power).bind(lambda a, b, c: test(a, b, c))


class TestDelayMonoid(TestCase):
    def pow(self, x: int):
        return x * x

    def double(self, x: int):
        return x * 2

    def half(self, x: int):
        return int(x / 2)

    def combine_func(self, a: Callable[[int], int], b: Callable[[int], int]):
        def wrapper(x: int):
            return b(a(x))

        return wrapper

    @note("딜레이 연결성 테스트")
    @note("딜레이는 이항연산이 가능해야됨")
    def test_monoid_has_connectivity(self):

        x = Delay(self.pow)
        y = Delay(self.double)
        z = Delay[[int], int].combined(x, y, self.combine_func)
        self.assertEqual(z.run(10), 200)

    @note(f"딜레이 항등원 테스트")
    @note(f"딜레이는 특정한 값 x가 있어 임의의 y에 대해 x*y == y*x = y를 만족해야됨")
    def test_monoid_has_identity(self):
        certain = Delay[[int], int].identity()
        random = Delay[[int], int].of(lambda x: x * 758)
        a = Delay[[int], int].combined(certain, random, self.combine_func)
        b = Delay[[int], int].combined(random, certain, self.combine_func)
        self.assertEqual(a.run(10), b.run(10))

    @note(f"딜레이 결합법칙 테스트")
    @note(f"딜레이는 x,y,z에 대해 (x*y)*z == x*(y*z)가 성립함")
    def test_delay_has_association(self):
        x, y, z = Delay(self.pow), Delay(self.double), Delay(self.half)
        left = x.combined(y, self.combine_func).combined(z, self.combine_func)
        right = x.combined(y.combined(z, self.combine_func), self.combine_func)
        self.assertEqual(left.run(20), right.run(20))
