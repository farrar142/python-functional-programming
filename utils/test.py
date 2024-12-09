from functools import wraps
from typing import Callable, ParamSpec, TypeVar


P = ParamSpec("P")
T = TypeVar("T")


def note(note: str):
    def decorator(callable: Callable[P, T]) -> Callable[P, T]:

        @wraps(callable)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                result = callable(*args, **kwargs)
                print(f"[O] {callable.__name__} : {note}")
                return result
            except Exception as e:
                print(f"[X]{callable.__name__} : {note}")
                raise e

        return wrapper

    return decorator


def pass_test(callable: Callable[P, T]) -> Callable[P, None]:
    @wraps(callable)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        return None

    return wrapper
