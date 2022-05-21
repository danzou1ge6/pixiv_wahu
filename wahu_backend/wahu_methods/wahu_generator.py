from typing import Any, Optional

from ..wahu_core import WahuArguments, WahuContext, wahu_methodize
from ..wahu_core.core_exceptions import WahuRuntimeError
from ..wahu_core.core_typing import GenericWahuMethod


async def _check_generator_key(m: GenericWahuMethod, args: WahuArguments, ctx: WahuContext):
    """检查是否提供 `generator key` 的中间件"""

    if 'key' not in args.keys():
        raise WahuRuntimeError(f'anext 缺少参数 key')

    return await m(args, ctx)


class WahuGeneratorMethods:
    @wahu_methodize(middlewares=[_check_generator_key])
    @staticmethod
    async def wahu_anext(ctx: WahuContext, key: str) -> Optional[Any]:
        """调用 `ctx.agenerator_pool` 中的异步生成器"""

        return await ctx.agenerator_pool.call(key)

    @wahu_methodize(middlewares=[_check_generator_key])
    @staticmethod
    async def wahu_dispose_generator(ctx: WahuContext, key: str) -> bool:
        """删除异步生成器"""

        return ctx.agenerator_pool.pop(key)
