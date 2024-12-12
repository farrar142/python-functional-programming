import functools
from typing import Callable, Literal, ParamSpec, TypeVar

from functor import Functor
from monoid import Monoid


P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
N = TypeVar("N")


class Result[T](Functor[T | Exception], Monoid[T | Exception]):
    @classmethod
    def of(cls, value: T | Exception):
        return cls(value)

    @classmethod
    def identity(cls) -> "Result[T]":
        return Failed[T].of(Exception())

    @classmethod
    def wraps(cls, func: Callable[P, N]) -> "Callable[P, Result[N]]":
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            try:
                return Success[N].of(func(*args, **kwargs))
            except Exception as e:
                return Failed.of(e)

        return wrapper

    def bind(self, callable: Callable[[T], N]) -> "Result[N]": ...

    def combined(
        self, other: "Result[U]", operator: Callable[[T, U], V]
    ) -> "Result[V]":
        if isinstance(self.value, Exception) or isinstance(other.value, Exception):
            return Result.identity()
        return Result.of(operator(self.value, other.value))

    def flat_bind(self, callable: "Callable[[T],Result[N]]") -> "Result[N]": ...
    def value_or(self, get: N) -> T | N: ...
    def value_or_throw(self, throw: Exception | type[Exception]) -> T: ...
    def value_or_get(self, get: Callable[[], N]) -> T | N: ...

    def __eq__(self, obj: "Result[U]"):
        eq = super().__eq__(obj)
        if eq:
            return eq
        if not isinstance(obj, self.__class__):
            return eq
        if isinstance(self.value, Exception) and isinstance(obj.value, Exception):
            return self.value.__class__ == obj.value.__class__
        return False


class Success(Result[T]):
    value: T

    def __init__(self, value: T):
        self.value = value

    def bind(self, callable: Callable[[T], N]) -> "Result[N]":
        try:
            return Success[N].of(callable(self.value))
        except Exception as e:
            return Failed[N].of(e)

    def flat_bind(self, callable: Callable[[T], Result[N]]) -> "Result[N]":
        return callable(self.value)

    def value_or(self, get: N) -> T:
        return self.value

    def value_or_get(self, get: Callable[[], N]) -> T:
        return self.value

    def value_or_throw(self, throw: Exception | type[Exception]) -> T:
        return self.value


class Failed(Result[T]):
    value: Exception

    def __init__(self, value: Exception):
        self.value = value

    def bind(self, callable: Callable[P, N]):
        return self

    def value_or(self, get: N) -> N:
        return get

    def value_or_get(self, get: Callable[[], N]) -> N:
        return get()

    def value_or_throw(self, throw: Exception | type[Exception]) -> T:
        raise throw

    def flat_bind(self, callable: Callable[[T], Result[N]]) -> "Result[N]":
        return Failed.of(self.value)
