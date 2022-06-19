import json
import aiohttp
from typing import Any, AsyncGenerator, Callable, Optional, TYPE_CHECKING, Sequence

from ..wahu_methods import WahuMethods

if TYPE_CHECKING:
    from inspect import Traceback

    from ..wahu_core import WahuContext
    WahuMethodsBase = WahuMethods
    WahuContextBase = WahuContext

else:
    WahuMethodsBase = object
    WahuContextBase = object



class WahuRemoteError(Exception):
    def __init__(self, err: str):
        self.err = err

    def __str__(self) -> str:
        return self.err


class WahuRemoteContext(WahuContextBase):
    """
    模拟一个远程 `WahuContext`

    （当然实际上访问不了实际的 `WahuContext`
    和 `WahuRemoteMethods` 搭配使用，模拟 `WahuMethod` 的语法
    """

    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url

    async def __aenter__(self) -> 'WahuRemoteContext':
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(
        self,
        excpt_type: Optional[type] = None,
        excpt_value: Optional[Exception] = None,
        excpt_tcbk: Optional['Traceback'] = None):

        await self.session.close()

        if excpt_value != None:
            raise excpt_value

    async def call(self, method: str, args: Sequence[Any]) -> Any:

        async with self.session.post(self.rpc_url, data=json.dumps({
            'method': method,
            'args': args
        })) as resp:

            ret = await resp.json()

        if ret['type'] == 'exception':
            raise WahuRemoteError(ret['return'])

        if ret['type'] == 'normal':
            return ret['return']

        if ret['type'] == 'generator':

            gen_key = ret['return']

            async def gen() -> AsyncGenerator[Any, Any]:
                send_val = None
                while True:
                    ret_val = await self.call(
                        'wahu_anext',
                        [gen_key, send_val]
                    )

                    if ret_val is None:
                        break

                    send_val = yield ret_val

            return gen()


class WahuRemoteMethodsType(WahuMethodsBase):
    """使用 POST RPC 接口和后端通信"""

    def __getattr__(self, name: str) -> Callable[..., Any]:

        async def f(ctx: WahuRemoteContext, *args: tuple[Any, ...]) -> Any:

            return await ctx.call(name, args)
        return f

WahuRemoteMethods = WahuRemoteMethodsType()  # __getattr__ 似乎不能作为 classmethod
