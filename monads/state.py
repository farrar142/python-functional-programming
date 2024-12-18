from typing import Callable, ParamSpec, TypeVar

from .functor import Functor


# 제너릭 타입 변수 정의
P = ParamSpec("P")
B = TypeVar("B")  # New Value


class State[S, A, C](Functor[Callable[[S], tuple[A, C]]]):
    """S값을 받으면 A의 결과, C의 값을 반환함"""

    def __init__(self, value: Callable[[S], tuple[A, C]]):
        self.value = value

    @classmethod
    def of(cls, value: A) -> "State[S, A, S]":
        return State(lambda state: (value, state))

    @classmethod
    def wraps(
        cls, func: "Callable[P,Callable[[S],tuple[A,C]]]"
    ) -> "Callable[P,State[S,A,C]]":
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            return cls(func(*args, **kwargs))

        return wrapper

    def run(self, initial_state: S) -> tuple[A, C]:
        return self.value(initial_state)

    def bind(self, func: Callable[[A], "State[C, A, B]"]) -> "State[S, A, B]":
        def new_run_state(state: S) -> tuple[A, B]:
            current_value, next_state = self.value(state)
            return func(current_value).value(next_state)

        return State(new_run_state)
