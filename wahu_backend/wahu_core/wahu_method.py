import inspect
from functools import partial
from itertools import chain
from typing import (TYPE_CHECKING, Any, Callable, Concatenate, Coroutine,
                    Generic, ParamSpec, Type, TypeVar)

from .core_exceptions import WahuMethodArgsKeyError, WahuMethodParseError
from .core_typing import WahuArguments, WahuMiddleWare
from .wahu_context import WahuContext

if TYPE_CHECKING:
    from ..wahu_methods import WahuMethods


def parse_func_args(f: Callable[..., Any]) -> list[str]:
    return list(inspect.signature(f).parameters.keys())


RT = TypeVar('RT')  # Return Type
P = ParamSpec('P')

class WahuMethod(Generic[RT, P]):
    """
    可以挂载到 `WahuMethods` 的一个 `Wahu` 方法 \n
    调用时，按照从左到右的顺序依次调用 `self.middle_wares`
    """

    def __init__(
        self,
        name: str,
        f: Callable[Concatenate['WahuMethods', P], Coroutine[None, None, RT]], *,
        middlewares: list[WahuMiddleWare[RT]]
    ):
        """
        - `:param name:` 方法的名称，用于在 `WahuMethods` 的解析中
        - `:param f:` 原始的函数，第一个参数位置留给 `WahuContext`
        - `:middlewares:` 要使用的中间件
        """
        self.name = name
        self.f = f
        self.middlewares = middlewares

        arg_names = parse_func_args(f)
        self.arg_names = arg_names[2:]

    async def rpc_f(
        self,
        cls: Type['WahuMethods'],
        args: WahuArguments,
        context: WahuContext
    ) -> RT:
        """
        传入 `args` 字典来调用原始的函数 `f`
        """

        try:
            args_tuple = tuple(chain(
                (cls, context,),
                (args[name] for name in self.arg_names)
            ))

        except KeyError as ke:
            raise WahuMethodArgsKeyError(f'{ke.args}') from ke

        return await self.f(*args_tuple)  # type: ignore

    async def call(
        self,
        cls: Type['WahuMethods'],
        args: WahuArguments,
        context: WahuContext
    ) -> RT:
        """
        在应用了所有中间件后调用 `rpc_f`
        - `:param args:` rpc 调用的字典
        - `:param context:` `WahuContext` 实例
        """

        hdlr = self.rpc_f
        for mw in self.middlewares:
            hdlr = partial(mw, hdlr)

        return await hdlr(cls, args, context)  # type: ignor

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> RT:
        """
        调用原始的函数 `f`
        cls 会被自动绑定
        """

        return await self.f(*args, **kwargs)  # type: ignore


def wahu_methodize(
    middlewares: list[WahuMiddleWare] = [],
) -> Callable[[Callable[Concatenate['WahuMethods', P], Coroutine[None, None, RT]]], WahuMethod[RT, P]]:
    """
    `WahuMethod` 的工厂函数，将一个异步函数转换为带有中间件的 `WahuMethod`
    """

    def f(g: Callable[Concatenate['WahuMethods', P], Coroutine[None, None, RT]]) -> WahuMethod[RT, P]:

        h = WahuMethod(
            g.__name__,
            g,
            middlewares=middlewares
        )

        return h

    return f
