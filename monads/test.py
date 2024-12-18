from functools import wraps
from typing import Callable, ParamSpec, TypeVar
from unittest import TestCase
from random import randint

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


from .monoid import Monoid


def generate_monoid_test(monoid_class: type[Monoid[int]]):
    Monoid = monoid_class

    class TestMonoid(TestCase):
        @note(f"{monoid_class} 연결성 테스트")
        @note(f"{monoid_class}는 이항연산이 가능해야됨")
        def test_monoid_has_connectivity(self):
            x = Monoid.of(5)
            y = Monoid.of(10)
            z = Monoid.combined(x, y, lambda x, y: x * y)
            self.assertEqual(z.value, 50)

        @note(f"{monoid_class} 항등원 테스트")
        @note(
            f"{monoid_class} 특정한 값 x가 있어 임의의 y에 대해 x*y == y*x = y를 만족해야됨"
        )
        def test_monoid_has_identity(self):
            certain = Monoid.identity()
            random = Monoid.of(randint(1, 100))
            a = Monoid.combined(certain, random, lambda x, y: x - y)
            b = Monoid.combined(random, certain, lambda x, y: x - y)
            self.assertEqual(a, b)
            a = Monoid.combined(certain, random, lambda x, y: x * y)
            b = Monoid.combined(random, certain, lambda x, y: x * y)
            self.assertEqual(a, b)

        @note(f"{monoid_class} 결합법칙 테스트")
        @note(f"{monoid_class}는 x,y,z에 대해 (x*y)*z == x*(y*z)가 성립함")
        def test_monoid_has_association(self):
            x, y, z = Monoid.of(2), Monoid.of(3), Monoid.of(6)
            multiplier: Callable[[int, int], int] = lambda x, y: x * y
            left = x.combined(y, multiplier).combined(z, multiplier)
            right = x.combined(y.combined(z, multiplier), multiplier)
            self.assertEqual(left, right)

    return TestMonoid


from .context import Context
from .maybe import Maybe
from .result import Result, Success, Failed
from .delay import Delay
from .state import State


class TestMaybe(TestCase):
    @note("메이비 생성 테스트")
    def test_1(self):
        maybe = Maybe.of(5)
        self.assertIsInstance(maybe, Maybe)

    @note("메이비 초기값 테스트")
    def test_2(self):
        maybe = Maybe.of(5)
        self.assertEqual(maybe.get(), 5)

    @note("메이비에 콜러블을 할당 할 수 있어야함")
    def test_3(self):
        maybe = Maybe.call(lambda: 5)
        self.assertEqual(maybe.get(), 5)

    @note("메이비는 map을 통해 새로운 메이비를 반환해야됨")
    def test_4(self):
        maybe = Maybe.of(5).map(lambda x: str(x))
        self.assertIsInstance(maybe, Maybe)
        self.assertEqual(maybe.get(), "5")

    @note("메이비의 map은 체이닝이 되어야됨")
    def test_5(self):
        maybe = Maybe.of(5).map(lambda x: str(x)).map(int)
        self.assertEqual(maybe.get(), 5)

    @note("메이비의 플랫맵은 옵셔널리턴값을 평탄화해야됨")
    def test_5_2(self):
        maybe = Maybe.of(5).map(lambda x: Maybe.of(5))
        self.assertIsInstance(maybe.get(), Maybe)
        maybe = Maybe.of(5).bind(lambda x: Maybe.of(5)).map(int)
        self.assertEqual(maybe.get(), 5)

    @note("메이비는 값 혹은 None을 반환해야됨")
    def test_6(self):
        maybe = Maybe.of(5)
        self.assertEqual(maybe.get(), 5)

    @pass_test
    @note("메이비는 value에 값을 접근 할 수 없어야됨")
    def test_7(self):
        maybe = Maybe.of(5)
        with self.assertRaises(Exception):
            maybe.value  # type:ignore

    @note("메이비의 or_else로 값이 None일시 대체 값을 반환해야됨")
    def test_8(self):
        maybe = Maybe[int].nothing()
        self.assertEqual(maybe.or_else(5), 5)

    @note("메이비의 or_else에 함수값이 필요 할 시 or_elseGet을 사용해야됨")
    def test_9(self):
        maybe = Maybe[int].nothing()
        self.assertEqual(maybe.or_else_get(lambda: 5), 5)

    @note("메이비의 or_else_get은 값이 있을 경우엔 실행되면 안됨")
    def test_10(self):
        maybe = Maybe[int].of(5)

        def get_func():
            raise Exception

        self.assertEqual(maybe.or_else_get(get_func), 5)

    @note("메이비의 or_else_get은 값이 없을 경우엔 실행되어야됨")
    def test_11(self):
        maybe = Maybe[int].nothing()

        def get_func():
            raise Exception

        with self.assertRaises(Exception):
            maybe.or_else_get(get_func)

    @note(
        "메이비에 값이 없을 경우에 error를 반환하는 메서드가 or_else_throw가 있어야됨"
    )
    def test_12(self):
        maybe = Maybe[int].nothing()
        with self.assertRaises(ZeroDivisionError):
            maybe.or_else_throw(ZeroDivisionError)

    @note("메이비에 값이 있을 경우에 or_else_throw는 에러를 반환하면 안됨")
    def test_13(self):
        maybe = Maybe.of(5)
        self.assertEqual(maybe.or_else_throw(Exception), 5)

    @note("메이비의 or_else_throw는 Exception 인스턴스도 받아야됨")
    def test_14(self):
        maybe = Maybe[int].nothing()
        with self.assertRaises(ZeroDivisionError):
            maybe.or_else_throw(ZeroDivisionError("인스턴스"))

    @note("메이비의 wraps는 함수를 데코레이션 해야됨")
    def test_15(self):
        @Maybe.wraps
        def wrapped(a: int, b: int) -> int | None:
            return a + b

        maybe = wrapped(1, 2)
        self.assertEqual(maybe.get(), 3)

    @note("메이비 왼쪽 항등법칙 테스트 Maybe.of(x).chain(f) == f(x) ")
    def test_16(self):
        @Maybe.wraps
        def square(a: int):
            return a * a

        left = Maybe.of(5).bind(square)
        right = square(5)
        self.assertEqual(left.or_else_throw(), 25)
        self.assertEqual(right.or_else_throw(), 25)
        self.assertEqual(left, right)

    @note(
        "메이비 오른쪽 항등법칙테스트 Maybe.of(x).chain(Maybe.of) == y === x.bind(Maybe.of)"
    )
    def test_17(self):
        @Maybe.wraps
        def square(a: int):
            return a * a

        left = Maybe.of(5).bind(square)
        right = left.bind(Maybe.of)
        self.assertEqual(left, right)

    @note(
        "메이비 결합법칙 테스트 Maybe(x).chain(f).chain(g) == Maybe(x).chain(x=>f(x).chain(g))가 성립해야된다"
    )
    def test_18(self):
        @Maybe.wraps
        def square(a: int):
            return a * a

        @Maybe.wraps
        def stringify(a: int):
            return str(a)

        left = Maybe.of(5).bind(square).bind(stringify)
        right = Maybe.of(5).bind(lambda x: square(x).bind(stringify))
        self.assertEqual(left.or_else_throw(), "25")
        self.assertEqual(right.or_else_throw(), "25")
        self.assertEqual(left, right)


TestMaybeMonoid = generate_monoid_test(Maybe)


class TestResult(TestCase):
    @Result.wraps
    def on_success(self):
        return 1

    @Result.wraps
    def on_failed(self) -> int:
        raise Exception

    @note("리절트는 성공했을때 Success를 반환해야됨")
    def test_1(self):
        self.assertIsInstance(self.on_success(), Success)

    @note("리절트는 실패했을때 Failed를 반환해야됨")
    def test_2(self):
        self.assertIsInstance(self.on_failed(), Failed)

    @note("리절트의 bind는 성공한 연산에 대해 값을 이어나가야됨")
    def test_3(self):
        result = self.on_success().bind(str)
        self.assertEqual(result.value, "1")

    @note("리절트의 bind는 실패한 연산에 대해 값을 이어나가지 않음")
    def test_4(self):
        result = self.on_failed().bind(str)
        self.assertIsInstance(result.value, Exception)

    @note("리절트가 Success일때 value_or을 쓰면 value값이 나와야됨")
    def test_5(self):
        result = self.on_success().value_or("5")
        self.assertEqual(result, 1)

    @note("리절트가 Failed일때 value_or을 쓰면 or값이 나와야됨")
    def test_6(self):
        result = self.on_failed().value_or(5)
        self.assertEqual(result, 5)

    @note("리절트의 map에 Result를 반환하면 Result가 중첩이 되어야됨")
    def test_7(self):
        result = self.on_success().bind(lambda x: self.on_success())
        self.assertIsInstance(result.value, Result)

    @note("리절트의 flat_bind는 중첩된 Result를 평탄화해야됨")
    def test_8(self):
        result = self.on_success().flat_bind(lambda x: self.on_success())
        self.assertIsInstance(result.value, int)

    @note("리절트의 flat_bind는 석세스가 실패할 때마다 새로운 Failed를 반환해야됨")
    def test_9(self):
        @Result.wraps
        def importerror() -> int:
            raise ImportError

        @Result.wraps
        def zdiverror() -> int:
            raise ZeroDivisionError

        result = self.on_success()
        r1 = result.flat_bind(lambda x: importerror())
        self.assertIsInstance(r1.value, ImportError)
        r2 = result.flat_bind(lambda x: zdiverror())
        self.assertIsInstance(r2.value, ZeroDivisionError)


TestResultMonoid = generate_monoid_test(Result)


class Container:
    def __init__(self, value: int):
        self.value = value

    def power(self):
        self.value = self.value * self.value
        return self


class TestDelay(TestCase):
    @note("딜레이는 함수를 감싸고, 최종 호출을 해야지 실행이됨")
    def test_1(self):
        @Delay
        def test(container: Container):
            container.value += 1

        container = Container(0)
        delayed = test(container)
        self.assertEqual(container.value, 0)
        delayed.run()
        self.assertEqual(container.value, 1)

    @note("딜레이끼리는 bind가 가능해야됨")
    def test_2(self):
        @Delay
        def increase(container: Container):
            container.value += 1
            return container

        def power(container: Container):
            def inner():
                container.value = container.value * container.value
                return container

            return Delay(inner)

        @Delay
        def test(container: Container):
            return container.value + 2

        container = Container(1)
        delay = increase(container).bind(power)
        self.assertEqual(container.value, 1)
        delay.run()
        self.assertEqual(container.value, 4)
        delay2 = increase.bind(power)
        self.assertEqual(container.value, 4)
        delay2.run(container)
        self.assertEqual(container.value, 25)
        container = Container(5)
        two = increase(container).bind(power).bind(increase)
        self.assertEqual(container.value, 5)
        two.run()
        self.assertEqual(container.value, 37)

        container = Container(3)
        three = power(container).bind(power).bind(test)
        self.assertEqual(container.value, 3)
        self.assertEqual(three.run(), 83)
        print(three)
        # increase.bind(power).bind(lambda a, b, c: test(a, b, c))


class TestDelayMonoid(TestCase):
    def pow(self, x: int):
        return x * x

    def double(self, x: int):
        return x * 2

    def half(self, x: int):
        return int(x / 2)

    def combine_func(self, a: Callable[[int], int], b: Callable[[int], int]):
        def wrapper(x: int):
            return b(a(x))

        return wrapper

    @note("딜레이 연결성 테스트")
    @note("딜레이는 이항연산이 가능해야됨")
    def test_monoid_has_connectivity(self):

        x = Delay(self.pow)
        y = Delay(self.double)
        z = Delay[[int], int].combined(x, y, self.combine_func)
        self.assertEqual(z.run(10), 200)

    @note(f"딜레이 항등원 테스트")
    @note(f"딜레이는 특정한 값 x가 있어 임의의 y에 대해 x*y == y*x = y를 만족해야됨")
    def test_monoid_has_identity(self):
        certain = Delay[[int], int].identity()
        random = Delay[[int], int].of(lambda x: x * 758)
        a = Delay[[int], int].combined(certain, random, self.combine_func)
        b = Delay[[int], int].combined(random, certain, self.combine_func)
        self.assertEqual(a.run(10), b.run(10))

    @note(f"딜레이 결합법칙 테스트")
    @note(f"딜레이는 x,y,z에 대해 (x*y)*z == x*(y*z)가 성립함")
    def test_delay_has_association(self):
        x, y, z = Delay(self.pow), Delay(self.double), Delay(self.half)
        left = x.combined(y, self.combine_func).combined(z, self.combine_func)
        right = x.combined(y.combined(z, self.combine_func), self.combine_func)
        self.assertEqual(left.run(20), right.run(20))


class TestState(TestCase):
    @note("스테이트는 bind를 하여 메서드를 체이닝 할 수 있어야함")
    def test_1(self):
        def multiply(a: int):
            return State[int, str, int](lambda value: ("multiply", a * value))

        State.of(25).bind(lambda _: multiply(5))

    @note("스테이트는 최종값과 상태를 run을 통해 가져 올 수 있어야함")
    def test_2(self):
        def power(state: str):
            return State[int, str, int](lambda value: ("multiply", value * value))

        def stringify(state: str):
            return State[int, str, str](lambda value: ("stringified", str(value)))

        state = State[int, str, int].of("initialized").bind(power).bind(stringify)
        value, final_state = state.run(5)
        self.assertEqual("stringified", value)
        self.assertEqual("25", final_state)

    @note("스테이트 실사용테스트")
    def test_3(self):
        def deposit(amount: int):
            return State[int, str, int](
                lambda balance: (f"{amount} 예금", balance + amount)
            )

        def withdraw(amount: int):
            return State[int, str, int](
                lambda balance: (
                    f"{amount} 출금",
                    balance - amount if balance >= amount else balance,
                )
            )

        # Monad 체인
        result = (
            deposit(500)
            .bind(lambda _: withdraw(200))
            .bind(lambda _: withdraw(1500))  # 잔액 부족한 경우
            .bind(lambda _: State[int, str, int].of("거래 완료"))
        )

        # 실행
        value, final_state = result.run(1000)
        self.assertEqual(value, "거래 완료")
        self.assertEqual(final_state, 1300)

    @note("스테이트는 wraps를 통하여 lambda 를 반환하는 함수를 감쌀수있어야함")
    def test_4(self):
        @State[int, str, int].wraps
        def deposit(amount: int):
            return lambda balance: (f"{amount} 예금", balance + amount)

        @State[int, str, int].wraps
        def withdraw(amount: int):
            return lambda balance: (
                f"{amount} 출금",
                balance - amount if balance >= amount else balance,
            )

        result = (
            deposit(500)
            .bind(lambda _: withdraw(200))
            .bind(lambda _: withdraw(1500))  # 잔액 부족한 경우
            .bind(lambda _: State[int, str, int].of("거래 완료"))
        )

        value, final_state = result.run(1000)
        self.assertEqual(value, "거래 완료")
        self.assertEqual(final_state, 1300)


class TestContext(TestCase):
    @note("컨텍스트는 컨텍스트를 인자로받는 콜백함수를 인자로 받아야됨")
    def test_1(self):
        def with_context():
            return Context(lambda context: context)

        self.assertIsInstance(with_context(), Context)

    @note("컨텍스트를 반환하는 함수는 실행했을시 콜러블을 반환해야됨")
    def test_2(self):
        def with_context():
            return Context(lambda context: context)

        self.assertTrue(callable(with_context()))

    @note("컨텍스트의 __call__은 컨텍스트를 주입받아서 콜백함수를 실행해야됨")
    def test_3(self):
        def with_context():
            return Context[int, int](lambda context: context)

        self.assertEqual(with_context()(1), 1)

    @note("컨텍스트를 데코레이터로 사용 가능 해야됨")
    def test_4(self):

        @Context[int, int].wraps
        def with_context(a: int, b: int):
            sum = a + b

            def context(x: int):
                return x + sum

            return context

        self.assertIsInstance(with_context(1, 2), Context)
        self.assertEqual(with_context(1, 2)(1), 4)

    @note(
        "컨텍스트에서 함수의 반환타입이 같고, 컨텍스트가 같으면 합성이 가능해야되는가?"
    )
    def test_5(self):
        @Context[int, int].wraps
        def sum(a: int):
            return lambda x: x + a

        @Context[int, int].wraps
        def multiply(a: int):
            return lambda x: x * a

        self.assertEqual(sum(1)(1), 2)
        self.assertEqual(multiply(2)(2), 4)
        sum_and_multiply = sum(1)(multiply(3)(2))
        self.assertEqual(sum_and_multiply, 7)
        sum_and_multiply = multiply(3).pipe(sum(1))(2)
        self.assertEqual(sum_and_multiply, 7)

        @Context[int, str].wraps
        def to_str():
            return lambda x: str(x)

        stringified = multiply(3).pipe(to_str())(3)
        self.assertEqual(stringified, "9")

    @note("같은 컨텍스트를 같지만 반환값이 다른 컨텍스트는 bind로 조합가능")
    def test_6(self):
        @Context[int, str].wraps
        def return_str(a: int):
            return lambda x: "fff"

        @Context[int, float].wraps
        def return_float(a: int):
            return lambda x: 10.5

        result = return_str(1).bind(return_float(1))(1)
        self.assertEqual(result, 10.5)

        @Context
        def what_ther(a: int):
            return lambda x: x * a

        result = what_ther(10)(5)
        print(result)
