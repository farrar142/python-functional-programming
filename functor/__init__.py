from typing import Self


class Functor[V]:
    value: V

    def __init__(self, value: V):
        self.value = value

    def __eq__(self, obj: Self):
        if self.__class__ == obj.__class__:
            return self.value == obj.value
        return False
