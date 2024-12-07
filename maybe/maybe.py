import functools
from typing import Callable, ParamSpec, Self, TypeVar

P = ParamSpec("P")
M = TypeVar("M")
N = TypeVar("N")


class Maybe[M]:
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
    def empty(cls, value: None) -> "Maybe[M]":
        return Maybe[M].of(value)

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

    def flat_map(self, callable: "Callable[[M],Maybe[N]]") -> "Maybe[N]":
        value = self.get()
        if value == None:
            return Maybe.of(None)
        new_value = callable(value)
        return new_value

    def orElse(self, orValue: M):
        value = self.get()
        if value:
            return value
        return orValue

    def orElseGet(self, orCallable: Callable[[], M]):
        value = self.get()
        if value:
            return value
        return orCallable()

    def orElseThrow(self, exception: type[Exception] | Exception = Exception) -> M:
        value = self.get()
        if value:
            return value
        raise exception

    def __eq__(self, obj: Self):
        if isinstance(obj, Maybe):
            return self.get() == obj.get()
        return False
