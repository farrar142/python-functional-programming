from unittest import TestCase

from delay.delay import Delay
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
