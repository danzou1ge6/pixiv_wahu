import ast
import inspect
from functools import partial
from itertools import chain
from typing import Any, Callable, Coroutine, Generic, Type, TypeVar

from .core_exceptions import WahuMethodArgsKeyError, WahuMethodParseError
from .core_typing import WahuArguments, WahuMethodsCollection, WahuMiddleWare
from .wahu_context import WahuContext


def parse_func_args(f: Callable[[Any], Any]) -> list[str]:
    tree = ast.parse(inspect.cleandoc(inspect.getsource(f)))

    if not isinstance(tree.body[0], ast.AsyncFunctionDef):
        raise WahuMethodParseError(f'解析函数定义 {f} 失败')

    return [arg.arg for arg in tree.body[0].args.args]


RT = TypeVar('RT')  # Return Type

class WahuMethod(Generic[RT]):
    """
    可以挂载到 `WahuMethodsCollection` 的一个 `Wahu` 方法 \n
    调用时，按照从左到右的顺序依次调用 `self.middle_wares`
    """

    def __init__(
        self,
        name: str,
        f: Callable[..., Coroutine[None, None, RT]], *,
        middlewares: list[WahuMiddleWare[RT]]
    ):
        """
        - `:param name:` 方法的名称，用于在 `WahuMethodsCollection` 的解析中
        - `:param f:` 原始的函数，第一个参数位置留给 `WahuContext`
        - `:middlewares:` 要使用的中间件
        """
        self.name = name
        self.f = f
        self.middlewares = middlewares

        arg_names = parse_func_args(f)
        self.arg_names = arg_names[2:]

    async def rpc_f(self, cls: Type[WahuMethodsCollection], args: WahuArguments, context: WahuContext) -> RT:
        try:
            args_tuple = tuple(chain(
                (cls, context,),
                (args[name] for name in self.arg_names)
            ))

        except KeyError as ke:
            raise WahuMethodArgsKeyError(f'{ke.args}') from ke

        return await self.f(*args_tuple)

    async def __call__(self, cls: Type[WahuMethodsCollection], args: WahuArguments, context: WahuContext) -> RT:
        """
        - `:param args:` rpc 调用的字典
        - `:param context:` `WahuContext` 实例
        """

        hdlr = self.rpc_f
        for mw in self.middlewares:
            hdlr = partial(mw, hdlr)

        return await hdlr(cls, args, context)


def wahu_methodize(
    middlewares: list[WahuMiddleWare] = [],
) -> Callable[[Callable[..., Coroutine[None, None, RT]]], WahuMethod[RT]]:
    """
    `WahuMethod` 的工厂函数，将一个异步函数转换为带有中间件的 `WahuMethod`
    """

    def f(g: Callable[..., Coroutine[None, None, RT]]) -> WahuMethod[RT]:

        h = WahuMethod(
            g.__name__,
            g,
            middlewares=middlewares
        )

        return h

    return f
