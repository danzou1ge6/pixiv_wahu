import asyncio
import json
import traceback
from typing import Any

import aiohttp
from aiohttp import WSMessage, web

from .. import constants
from ..http_typing import JSONItem
from ..wahu_core import WahuContext, WahuMethod
from ..wahu_methods import WahuMethods
from .obj2jsonizeable import jsonizeablize
from .transform_args import trans_args


"""
Wahu POST RPC 协议：
请求格式：
    - method: str 方法名 e.g. `ilst_bmdb.list_bm`
    - args: dict 参数字典 e.g. {'name': 'danzou1ge6', 'iid': 12345678}

返回格式：
    - type:
        'generator': 返回异步生成器
        'normal': 返回 JSON 数据
        'error': 返回错误的 traceback 字符串
    - return:
        | 若 `type` 为 `normal` ，为 JSON ，否则为一个或若干个 `key` ，用于方法
        | `anext` 的 `args` 中

Wahu WebSocket RPC 协议：
请求格式：
    - method: str 方法名
    - args: dict 参数字典
    - mcid: int 标识每一次调用
返回格式:
    - type:
        'generator': 返回异步生成器
        'normal': 返回 JSON 数据
        'failure': 调用失败
    - mcid: int 标识每一次调用
    - return:
        当 type='generator' 或 'normal' 和 POST RPC 一样
        当 type='failure' 返回 [异常类名, 异常的字符串表示]
"""


async def handle_call(
    method: WahuMethod,
    args_json: list[JSONItem],
    ctx: WahuContext
) -> tuple[str | list[str] | None, Any]:

    args = trans_args(method.paras, args_json)

    method_ret = await method.apply_mdw_call(WahuMethods, args, ctx)

    # 处理生成器
    if hasattr(method_ret, '__anext__'):
        gen_key = ctx.agenerator_pool.new(method_ret)
        return gen_key, None


    if isinstance(method_ret, tuple) and all(hasattr(item, '__anext__') for item in method_ret):
        gen_key_list = [ctx.agenerator_pool.new(gen) for gen in method_ret]
        return gen_key_list, None


    json_ret = jsonizeablize(method_ret)
    return None, json_ret



class WsMsgHandler:
    """
    处理每一个 ws 连接
    """

    def __init__(self, ws: web.WebSocketResponse, app: web.Application, ctx: WahuContext):
        self.ws = ws
        self.app = app
        self.ctx = ctx

        self.gen_key_record = []  # 记录与当前 ws 连接有关的生成器 key

    async def handle(self, msg: WSMessage) -> None:

        if msg.type == aiohttp.WSMsgType.TEXT:

            req = json.loads(msg.data)
            mcid = req['mcid']

            try:
                method_name = req['method']
                method = getattr(WahuMethods, method_name)
                args = req['args']

                if method.logged:
                    self.app.logger.info(
                        'Call[WS][%s]: %s(%s)'
                        % (mcid, method_name, _cut_string(args, self.ctx.config.log_rpc_ret_length))
                    )

                gen_related, ret = await handle_call(
                    method,
                    args,
                    self.ctx
                )

                if gen_related is not None:
                    resp = {
                        'type': 'generator',
                        'return': gen_related,
                        'mcid': mcid
                    }
                    if isinstance(gen_related, list):
                        self.gen_key_record += gen_related
                    else:
                        self.gen_key_record.append(gen_related)

                    if method.logged:
                        self.app.logger.info(
                            'Return[WS][%s]: [Generator]%s' % (mcid, gen_related)
                        )

                else:
                    resp = {
                        'type': 'normal',
                        'return': ret,
                        'mcid': mcid
                    }

                    if method.logged:
                        self.app.logger.info(
                            'Return[WS][%s]: %s'
                            % (mcid,
                               _cut_string(
                                json.dumps(ret, ensure_ascii=False),
                                self.ctx.config.log_rpc_ret_length
                            ))
                        )

                await self.ws.send_str(json.dumps(resp))

            except Exception as excp:

                resp = {
                    'type': 'failure',
                    'mcid': mcid,
                    'return': [
                        type(excp).__name__, str(excp)
                    ]
                }
                self.app.logger.error(str(excp) + '\n' + traceback.format_exc())

                await self.ws.send_str(json.dumps(resp))

    def clear_related_gen(self):
        for key in self.gen_key_record:
            self.ctx.agenerator_pool.pop(key)


def _cut_string(s: object, size: int):
    s = str(s)
    if len(s) <= size:
        return s
    else:
        return s[:size] + f' ...({len(s)} chars)'

def register(app: web.Application, ctx: WahuContext) -> None:

    routes = web.RouteTableDef()

    @routes.post(constants.postRPCURL)
    async def postrpc(req: web.Request) -> web.Response:
        """POST 方法 RPC 接口"""

        rpc_req = await req.json()

        try:
            method_name = req['method']
            method = getattr(WahuMethods, method_name)
            args = req['args']

            if method.logged:
                app.logger.info(
                    'Call[POST]: %s(%s)'
                    % (method_name, _cut_string(args, ctx.config.log_rpc_ret_length))
                )

            gen_related, ret = await handle_call(
                method,
                args,
                ctx
            )

            if gen_related is not None:
                rpc_resp = {
                    'type': 'generator',
                    'return': gen_related
                }
                if method.logged:
                    app.logger.info(
                        'Return[POST]: [Generator]%s' % gen_related
                    )
            else:
                rpc_resp = {
                    'type': 'normal',
                    'return': ret
                }
                if method.logged:
                    app.logger.info(
                        'Return[POST]: %s'
                        % _cut_string(json.dumps(ret, ensure_ascii=False), ctx.config.log_rpc_ret_length)
                    )

            resp_text = json.dumps(rpc_resp)

        except Exception as excp:
            resp_text = json.dumps({
                'type': 'error', 'return': traceback.format_exc()
            })
            app.logger.error(str(excp) + '\n' + traceback.format_exc())

        resp = web.Response(text=resp_text, content_type='application/json')

        return resp

    @routes.get(constants.wsRPCURL)
    async def wsrpc(req: web.Request) -> web.WebSocketResponse:
        """WebSocket RPC 接口"""

        ws = web.WebSocketResponse()
        await ws.prepare(req)

        app['ws'] = ws
        app.logger.info('Backend: WS RPC 已连接')

        handler = WsMsgHandler(ws, app, ctx)

        async for msg in ws:
            asyncio.create_task(handler.handle(msg))

        app.logger.warning('Backend: WS RPC 已关闭')
        handler.clear_related_gen()

        return ws

    app.add_routes(routes)
