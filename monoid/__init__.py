from typing import Callable, Self, TypeVar

U = TypeVar("U")
V = TypeVar("V")


class Monoid[T]:

    @classmethod
    def identity(cls) -> Self: ...

    """항등원이 있어야됨."""

    def bind(self, func: Callable[[T], "Monoid[U]"]) -> "Monoid[U]": ...

    def combined(
        self, other: "Monoid[U]", operator: "Callable[[T,U],V]"
    ) -> "Monoid[V]": ...
