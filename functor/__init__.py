from typing import Self, TypeVar


class Functor[V]:
    """
    Functor란 범주 A와 B 에 있어 A를 B로 변화시키는 것이다.
    ex) 1 * Functor = "1"
    ex) [1,2,3] * Functor => {1:1,2:2,3:3}
    ex) [1,2,3] => Functor<[1,4,9]>
    Endofunctor 범주 A를 다시 범주 A로 변환시킨다
    ex) 1 * Endofunctor => 1
    ex) [1,2,3] * Endofunctor => [1,2,3]
    ex) [1,2,3] * Endofunctor => [1,4,9]
    ex) Maybe * Endofunctor => Maybe
    """

    value: V

    def __init__(self, value: V):
        self.value = value

    def __eq__(self, obj: object):
        if isinstance(obj, self.__class__):
            return self.value == obj.value
        return False

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self.value}>"
