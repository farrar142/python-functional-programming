from typing import Callable, Self, TypeVar

U = TypeVar("U")
V = TypeVar("V")


class Monoid[T]:
    def __init__(self, value: T):
        self.value = value

    @classmethod
    def of(cls, value: T):
        return cls(value)

    @classmethod
    def identity(cls) -> Self: ...

    """항등원이 있어야됨."""

    def bind(self, func: Callable[[T], "Monoid[U]"]) -> "Monoid[U]": ...

    """이항연산정의"""

    def combined(
        self, other: "Monoid[U]", operator: "Callable[[T,U],V]"
    ) -> "Monoid[V]": ...

    """이항연산정의"""
