import json
import traceback

import aiohttp
from aiohttp import web

from .. import constants
from ..wahu_core import WahuContext
from .rpc_methods_handler import handle_rpc_call

"""
后端的 RPC 端口
"""


def _cut_string(s: str, size: int):
    if len(s) <= size:
        return s
    else:
        return s[:size] + f' ...({len(s)} chars)'

def register(app: web.Application, ctx: WahuContext) -> None:

    routes = web.RouteTableDef()

    @routes.post(constants.postRPCURL)
    async def postrpc(req: web.Request) -> web.Response:
        """POST 方法 RPC 接口 详见 `rpc_handler.py`"""

        data = await req.json()

        app.logger.debug('Backend: POST RPC 调用: %s' % data)

        try:
            ret = await handle_rpc_call(data, ctx)
            jret = json.dumps(ret, ensure_ascii=False)

            app.logger.debug('Backend: POST RPC 返回: %s' % _cut_string(jret,
                                                                    ctx.config.log_rpc_ret_length))


        except Exception as e:
            jret = json.dumps({
                'type': 'exception', 'return': traceback.format_exc()
            })

            app.logger.exception(e, exc_info=True)

        resp = web.Response(text=jret, content_type='application/json')

        return resp

    @routes.get(constants.wsRPCURL)
    async def wsrpc(req: web.Request) -> web.WebSocketResponse:
        """WebSocket RPC 接口 详见 `rpc_handler.py`"""

        ws = web.WebSocketResponse()
        await ws.prepare(req)

        app['ws'] = ws
        app.logger.info('Backend: WS RPC 已连接')

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:

                jdata = json.loads(msg.data)
                app.logger.debug('Backend: WS RPC 调用: %s' % jdata)

                mcid = jdata['mcid']

                try:
                    ret = await handle_rpc_call(jdata, ctx)
                    ret['mcid'] = mcid

                    jret = json.dumps(ret, ensure_ascii=False)
                    app.logger.debug(
                        'Backend: WS RPC 返回: %s' % _cut_string(jret,
                                                                ctx.config.log_rpc_ret_length))
                    await ws.send_str(jret)

                except Exception as excp:

                    ret = {
                        'type': 'failure',
                        'mcid': mcid
                    }

                    await ws.send_str(json.dumps(ret))
                    app.logger.exception(excp, exc_info=True)

        app.logger.warning('Backend: WS RPC 已关闭')

        return ws

    app.add_routes(routes)
