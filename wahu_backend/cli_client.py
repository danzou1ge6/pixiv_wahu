import json
import os
import aiohttp
from pathlib import Path
from typing import Any, AsyncGenerator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from inspect import Traceback

from wahu_backend.wahu_config import load_config
from wahu_backend.constants import postRPCURL


class WahuRemoteError(Exception):
    def __init__(self, err: str):
        self.err = err

    def __str__(self) -> str:
        return self.err


class WahuRPCClient:
    """使用 POST RPC 接口和后端通信"""

    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url

    async def __aenter__(self) -> 'WahuRPCClient':
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

    async def call(self, method: str, args: dict[str, Any]) -> Any:

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
                        {'key': gen_key, 'send_val': send_val}
                    )

                    if ret_val is None:
                        break

                    send_val = yield ret_val

            return gen()


async def main(args: list[str]):
    conf_path = os.environ.get('PIXIVWAHU_CONFPATH')

    if conf_path is None:
        raise EnvironmentError('环境变量 PIXIVWAHU_CONFPATH 不存在')

    conf = load_config(Path(conf_path))

    backend_host = '127.0.0.1' if conf.server_host == '0.0.0.0' else conf.server_host
    rpc_url = f'http://{backend_host}:{conf.server_port}{postRPCURL}'

    async with WahuRPCClient(rpc_url) as client:

        try:

            agen: AsyncGenerator[str, str | None] = await client.call(
                'wahu_client_exec',
                {'args': args}
            )

            send_val = None
            while True:
                try:
                    val = await agen.asend(send_val)

                    if val is None:
                        break

                    else:
                        if val == '[:input]':
                            send_val = input()
                        else:
                            print(val, end='', flush=True)

                except StopAsyncIteration:
                    break

        except WahuRemoteError as wre:
            print(wre)
            return 1

    return 0



