import functools
from typing import Callable, Literal, ParamSpec, TypeVar

from functor import Functor


P = ParamSpec("P")
T = TypeVar("T")
N = TypeVar("N")


class Result[T](Functor[T]):
    __cls_key = object()
    value: T | Exception

    def __init__(self, key: object, value: T | Exception):
        assert (
            key == self.__class__.__cls_key
        ), "You cannot initialize Result by __init__, use Result.of(value)"

    @classmethod
    def of(cls, value: T | Exception):
        return cls(cls.__cls_key, value)

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
    def flat_bind(self, callable: "Callable[[T],Result[N]]") -> "Result[N]": ...
    def value_or(self, get: N) -> T | N: ...
    def value_or_throw(self, throw: Exception | type[Exception]) -> T: ...
    def value_or_get(self, get: Callable[[], N]) -> T | N: ...


class Success(Result[T]):
    value: T

    def __init__(self, key: object, value: T):
        self.value = value
        super().__init__(key, value)

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

    def __init__(self, key: object, value: Exception):
        self.value = value
        super().__init__(key, value)

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
