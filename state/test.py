from unittest import TestCase

from utils.test import note

from .state import State


class TestState(TestCase):
    @note("스테이트는 bind를 하여 메서드를 체이닝 할 수 있어야함")
    def test_1(self):
        def multiply(a: int):
            return State[int, str, int](lambda value: ("multiply", a * value))

        State.of(25).bind(lambda _: multiply(5))

    @note("스테이트는 최종값과 상태를 run을 통해 가져 올 수 있어야함")
    def test_2(self):
        def power(state: str):
            return State[int, str, int](lambda value: ("multiply", value * value))

        def stringify(state: str):
            return State[int, str, str](lambda value: ("stringified", str(value)))

        state = State[int, str, int].of("initialized").bind(power).bind(stringify)
        value, final_state = state.run(5)
        self.assertEqual("stringified", value)
        self.assertEqual("25", final_state)

    @note("스테이트 실사용테스트")
    def test_3(self):
        def deposit(amount: int):
            return State[int, str, int](
                lambda balance: (f"{amount} 예금", balance + amount)
            )

        def withdraw(amount: int):
            return State[int, str, int](
                lambda balance: (
                    f"{amount} 출금",
                    balance - amount if balance >= amount else balance,
                )
            )

        # Monad 체인
        result = (
            deposit(500)
            .bind(lambda _: withdraw(200))
            .bind(lambda _: withdraw(1500))  # 잔액 부족한 경우
            .bind(lambda _: State[int, str, int].of("거래 완료"))
        )

        # 실행
        value, final_state = result.run(1000)
        self.assertEqual(value, "거래 완료")
        self.assertEqual(final_state, 1300)

    @note("스테이트는 wraps를 통하여 lambda 를 반환하는 함수를 감쌀수있어야함")
    def test_4(self):
        @State[int, str, int].wraps
        def deposit(amount: int):
            return lambda balance: (f"{amount} 예금", balance + amount)

        @State[int, str, int].wraps
        def withdraw(amount: int):
            return lambda balance: (
                f"{amount} 출금",
                balance - amount if balance >= amount else balance,
            )

        result = (
            deposit(500)
            .bind(lambda _: withdraw(200))
            .bind(lambda _: withdraw(1500))  # 잔액 부족한 경우
            .bind(lambda _: State[int, str, int].of("거래 완료"))
        )

        value, final_state = result.run(1000)
        self.assertEqual(value, "거래 완료")
        self.assertEqual(final_state, 1300)
