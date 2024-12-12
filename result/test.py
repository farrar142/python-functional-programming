from unittest import TestCase

from monoid.test import generate_monoid_test
from result.result import Success, Failed, Result
from utils.test import note


class TestResult(TestCase):
    @Result.wraps
    def on_success(self):
        return 1

    @Result.wraps
    def on_failed(self) -> int:
        raise Exception

    @note("리절트는 성공했을때 Success를 반환해야됨")
    def test_1(self):
        self.assertIsInstance(self.on_success(), Success)

    @note("리절트는 실패했을때 Failed를 반환해야됨")
    def test_2(self):
        self.assertIsInstance(self.on_failed(), Failed)

    @note("리절트의 bind는 성공한 연산에 대해 값을 이어나가야됨")
    def test_3(self):
        result = self.on_success().bind(str)
        self.assertEqual(result.value, "1")

    @note("리절트의 bind는 실패한 연산에 대해 값을 이어나가지 않음")
    def test_4(self):
        result = self.on_failed().bind(str)
        self.assertIsInstance(result.value, Exception)

    @note("리절트가 Success일때 value_or을 쓰면 value값이 나와야됨")
    def test_5(self):
        result = self.on_success().value_or("5")
        self.assertEqual(result, 1)

    @note("리절트가 Failed일때 value_or을 쓰면 or값이 나와야됨")
    def test_6(self):
        result = self.on_failed().value_or(5)
        self.assertEqual(result, 5)

    @note("리절트의 map에 Result를 반환하면 Result가 중첩이 되어야됨")
    def test_7(self):
        result = self.on_success().bind(lambda x: self.on_success())
        self.assertIsInstance(result.value, Result)

    @note("리절트의 flat_bind는 중첩된 Result를 평탄화해야됨")
    def test_8(self):
        result = self.on_success().flat_bind(lambda x: self.on_success())
        self.assertIsInstance(result.value, int)

    @note("리절트의 flat_bind는 석세스가 실패할 때마다 새로운 Failed를 반환해야됨")
    def test_9(self):
        @Result.wraps
        def importerror() -> int:
            raise ImportError

        @Result.wraps
        def zdiverror() -> int:
            raise ZeroDivisionError

        result = self.on_success()
        r1 = result.flat_bind(lambda x: importerror())
        self.assertIsInstance(r1.value, ImportError)
        r2 = result.flat_bind(lambda x: zdiverror())
        self.assertIsInstance(r2.value, ZeroDivisionError)


TestResultMonoid = generate_monoid_test(Result)
