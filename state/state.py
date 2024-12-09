from typing import Callable, ParamSpec, TypeVar


# 제너릭 타입 변수 정의
P = ParamSpec("P")
B = TypeVar("B")  # New Value


class State[S, A, C]:
    """S값을 받으면 A의 결과, C의 값을 반환함"""

    def __init__(self, runnable_state: Callable[[S], tuple[A, C]]):
        self.runnable_state = runnable_state

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
        return self.runnable_state(initial_state)

    def bind(self, func: Callable[[A], "State[C, A, B]"]) -> "State[S, A, B]":
        def new_run_state(state: S) -> tuple[A, B]:
            current_value, next_state = self.runnable_state(state)
            return func(current_value).runnable_state(next_state)

        return State(new_run_state)