import shutil
import aiohttp

from ..constants import postRPCURL
from ..wahu_config import WahuConfig
from .remote import WahuRemoteMethods as WahuMethods, WahuRemoteContext, WahuRemoteError



async def main(args: list[str], conf: WahuConfig):

    backend_host = '127.0.0.1' if conf.server_host == '0.0.0.0' else conf.server_host
    rpc_url = f'http://{backend_host}:{conf.server_port}{postRPCURL}'

    async with WahuRemoteContext(rpc_url) as ctx:

        try:

            agen = await WahuMethods.wahu_client_exec(ctx, args, shutil.get_terminal_size())

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
                            send_val = None
                            print(val, end='', flush=True)

                except StopAsyncIteration:
                    break

        except WahuRemoteError as wre:
            print(wre)
            return 1

        except aiohttp.ClientConnectorError as e:
            print(f'无法连接后端: {str(e)}')
            return 1

    return 0



