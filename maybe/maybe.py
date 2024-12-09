from abc import ABC, abstractmethod
import functools
from typing import Callable, ParamSpec, Self, TypeVar

from functor import Functor

P = ParamSpec("P")
M = TypeVar("M")
N = TypeVar("N")


class Maybe[M](Functor[M]):
    __cls_key = object()
    __value: M | None

    def __init__(self, key: object, value: M | None):
        assert (
            key == self.__class__.__cls_key
        ), "You cannot initialize Maybe by __init__, use Maybe.of(value)"
        self.__value = value

    @classmethod
    def of(cls, value: N | None) -> "Maybe[N]":
        return Maybe(cls.__cls_key, value)

    @classmethod
    def just(cls, value: N) -> "Maybe[N]":
        return Maybe[N].of(value)

    @classmethod
    def nothing(cls) -> "Maybe[M]":
        return Maybe[M].of(None)

    @classmethod
    def call(cls, callable: Callable[[], N]) -> "Maybe[N]":
        try:
            return Maybe.of(callable())
        except:
            return Maybe.of(None)

    @classmethod
    def wraps(cls, callable: Callable[P, N | None]) -> "Callable[P,Maybe[N]]":
        @functools.wraps(callable)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            return Maybe.of(callable(*args, **kwargs))

        return wrapper

    def get(self):
        return self.__value

    def map(self, callable: Callable[[M], N]) -> "Maybe[N]":
        value = self.get()
        if value == None:
            return Maybe.of(None)
        new_value = callable(value)
        return Maybe.of(new_value)

    def bind(self, func: "Callable[[M], Maybe[N]]") -> "Maybe[N]":
        value = self.get()
        if value == None:
            return Maybe.nothing()
        return func(value)

    def or_else(self, orValue: N) -> "M|N":
        value = self.get()
        if value:
            return value
        return orValue

    def or_else_get(self, orCallable: Callable[[], M]):
        value = self.get()
        if value:
            return value
        return orCallable()

    def or_else_throw(self, exception: type[Exception] | Exception = Exception) -> M:
        value = self.get()
        if value:
            return value
        raise exception

    def __eq__(self, obj: Self):
        if isinstance(obj, Maybe):
            return self.get() == obj.get()
        return False
