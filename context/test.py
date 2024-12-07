from unittest import TestCase

from utils.test import note

from .context import Context


class TestContext(TestCase):
    @note("컨텍스트는 컨텍스트를 인자로받는 콜백함수를 인자로 받아야됨")
    def test_1(self):
        def with_context():
            return Context(lambda context: context)

        self.assertIsInstance(with_context(), Context)

    @note("컨텍스트를 반환하는 함수는 실행했을시 콜러블을 반환해야됨")
    def test_2(self):
        def with_context():
            return Context(lambda context: context)

        self.assertTrue(callable(with_context()))

    @note("컨텍스트의 __call__은 컨텍스트를 주입받아서 콜백함수를 실행해야됨")
    def test_3(self):
        def with_context():
            return Context[int, int](lambda context: context)

        self.assertEqual(with_context()(1), 1)

    @note("컨텍스트를 데코레이터로 사용 가능 해야됨")
    def test_4(self):

        @Context[int, int].wraps
        def with_context(a: int, b: int):
            sum = a + b

            def context(x: int):
                return x + sum

            return context

        self.assertIsInstance(with_context(1, 2), Context)
        self.assertEqual(with_context(1, 2)(1), 4)

    @note(
        "컨텍스트에서 함수의 반환타입이 같고, 컨텍스트가 같으면 합성이 가능해야되는가?"
    )
    def test_5(self):
        @Context[int, int].wraps
        def sum(a: int):
            return lambda x: x + a

        @Context[int, int].wraps
        def multiply(a: int):
            return lambda x: x * a

        self.assertEqual(sum(1)(1), 2)
        self.assertEqual(multiply(2)(2), 4)
        sum_and_multiply = sum(1)(multiply(3)(2))
        self.assertEqual(sum_and_multiply, 7)
        sum_and_multiply = multiply(3).compose(sum(1))(2)
        self.assertEqual(sum_and_multiply, 7)

        @Context[int, str].wraps
        def to_str():
            return lambda x: str(x)

        stringified = multiply(3).compose(to_str())(3)
        self.assertEqual(stringified, "9")
