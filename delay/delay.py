from typing import Callable, Generic, ParamSpec, TypeVar

from functor import Functor


P = ParamSpec("P")
Q = ParamSpec("Q")
T = TypeVar("T")
N = TypeVar("N")


class Delay(Functor[Callable[P, T]], Generic[P, T]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs):
        return Delay(lambda: self.value(*args, **kwargs))

    def run(self, *args: P.args, **kwargs: P.kwargs):
        return self.value(*args, **kwargs)

    def bind(self, delay: "Callable[[T],Delay[[],N]]") -> "Delay[P,N]":
        def combine(*args: P.args, **kwargs: P.kwargs) -> N:
            t_value = self.run(*args, **kwargs)
            return delay(t_value).run()

        return Delay[P, N](combine)

    def __repr__(self) -> str:
        return self.value.__repr__()
