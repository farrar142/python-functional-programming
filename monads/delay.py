from typing import Callable, Generic, ParamSpec, TypeVar

from .functor import Functor
from .monoid import Monoid


P = ParamSpec("P")
Q = ParamSpec("Q")
T = TypeVar("T")
N = TypeVar("N")


class Delay(Functor[Callable[P, T]], Monoid[Callable[P, T]]):
    @classmethod
    def of(cls, func: Callable[P, T]):
        return cls(func)

    @classmethod
    def identity(cls) -> "Delay[[N],N]":
        return Delay(lambda x: x)

    def __call__(self, *args: P.args, **kwargs: P.kwargs):
        return Delay(lambda: self.value(*args, **kwargs))

    def run(self, *args: P.args, **kwargs: P.kwargs):
        return self.value(*args, **kwargs)

    def map(self, func: "Callable[[T],N]") -> "Delay[P,N]":
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> N:
            t_value = self.run(*args, **kwargs)
            return func(t_value)

        return Delay[P, N](wrapper)

    def bind(self, delay: "Callable[[T],Delay[[],N]]") -> "Delay[P,N]":
        def combine(*args: P.args, **kwargs: P.kwargs) -> N:
            t_value = self.run(*args, **kwargs)
            return delay(t_value).run()

        return Delay[P, N](combine)

    def combined(
        self,
        other: "Delay[[T],N]",
        operator: Callable[[Callable[P, T], Callable[[T], N]], Callable[P, N]],
    ):
        return Delay(operator(self.value, other.value))

    def __repr__(self) -> str:
        return self.value.__repr__()
