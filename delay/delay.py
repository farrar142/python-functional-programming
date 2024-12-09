from functools import update_wrapper, wraps
from typing import Callable, Generic, ParamSpec, TypeVar


P = ParamSpec("P")
Q = ParamSpec("Q")
T = TypeVar("T")
N = TypeVar("N")


class Delay(Generic[P, T]):
    def __init__(self, func: Callable[P, T]):
        self.func = func

    def __call__(self, *args: P.args, **kwargs: P.kwargs):
        return Delay(lambda: self.func(*args, **kwargs))

    def run(self, *args: P.args, **kwargs: P.kwargs):
        return self.func(*args, **kwargs)

    def bind(self, delay: "Callable[[T],Delay[[],N]]") -> "Delay[P,N]":
        def combine(*args: P.args, **kwargs: P.kwargs) -> N:
            t_value = self.run(*args, **kwargs)
            return delay(t_value).run()

        return Delay[P, N](combine)

    def __repr__(self) -> str:
        return self.func.__repr__()
