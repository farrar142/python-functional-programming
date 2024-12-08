import functools
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
# C = TypeVar("C")
T = TypeVar("T")
N = TypeVar("N")


class Context[C, T]:
    def __init__(self, func: Callable[[C], T]):
        self.__func = func

    def __call__(self, context: C):
        return self.__func(context)

    @classmethod
    def wraps(
        cls, callable: Callable[P, Callable[[C], T]]
    ) -> "Callable[P,Context[C,T]]":
        @functools.wraps(callable)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> "Context[C,T]":
            return Context(callable(*args, **kwargs))

        return wrapper

    def bind(self, other: "Context[C,N]"):
        def wrapper(context: C):
            self(context)
            return other(context)

        return Context[C, N](wrapper)

    def pipe(self, other: "Context[T,N]"):
        return Context[C, N](lambda c: other(self(c)))
