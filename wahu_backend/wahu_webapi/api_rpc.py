import json
import traceback

import aiohttp
from aiohttp import web

from .. import constants
from ..http_typing import HTTPData, JSONItem
from ..wahu_core import WahuContext, WahuMethod
from ..wahu_methods import WahuMethods
from .obj2jsonizeable import jsonizeablize
from .transform_args import trans_args
from .webapi_exceptions import WahuWebAPIRPCCallError


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
        | 若 `type` 为 `normal` ，为 JSON ，否则为一个 `key` ，用于方法
        | `anext` 的 `args` 中

Wahu WebSocket RPC 协议：
被动：
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

主动：
    - type:
        'warning': 日志警告
        'error': 日志错误
        'dl_progress': 下载进度
    - return:
        当 type='warning' 或 'error' 返回日志的字符串表示
        当 type='dl_progress 返回 JSON 化的 `list[DownloadProgress]`
"""


async def handle_rpc_call(rpc_dict: HTTPData, ctx: WahuContext) -> dict[str, JSONItem]:
    """处理一个rpc请求，返回一个可以 JSON 化的对象"""


    try:

        method_name = rpc_dict['method']
        args_jsonitem = rpc_dict['args']

    except KeyError as e:
        raise WahuWebAPIRPCCallError('参数 method 或 dict 缺失') from e

    if not isinstance(method_name, str):
        raise WahuWebAPIRPCCallError('参数 method 应为 str')

    if not isinstance(args_jsonitem, list):
        raise WahuWebAPIRPCCallError('参数 args 应为 list')

    method: WahuMethod = getattr(WahuMethods, method_name)

    args = trans_args(method.paras, args_jsonitem)

    method_ret = await method.apply_mdw_call(WahuMethods, args, ctx)

    # 处理生成器
    if hasattr(method_ret, '__anext__'):
        gen_key = ctx.agenerator_pool.new(method_ret)

        return {'type': 'generator', 'return': gen_key}

    json_ret = jsonizeablize(method_ret)

    return {'type': 'normal', 'return': json_ret}


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
        """POST 方法 RPC 接口"""

        data = await req.json()

        app.logger.debug('Backend: POST RPC 调用: %s' % data)

        try:
            ret = await handle_rpc_call(data, ctx)
            jret = json.dumps(ret, ensure_ascii=False)

            app.logger.debug('Backend: POST RPC 返回: %s' % _cut_string(
                jret.replace('\x1b', '\\x1b').replace('\r', '\\r'),
                ctx.config.log_rpc_ret_length)
            )


        except Exception as e:
            jret = json.dumps({
                'type': 'error', 'return': traceback.format_exc()
            })

            app.logger.exception(e, exc_info=True)

        resp = web.Response(text=jret, content_type='application/json')

        return resp

    @routes.get(constants.wsRPCURL)
    async def wsrpc(req: web.Request) -> web.WebSocketResponse:
        """WebSocket RPC 接口"""

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
                        'mcid': mcid,
                        'return': [
                            type(excp).__name__, str(excp)
                        ]
                    }

                    await ws.send_str(json.dumps(ret))
                    app.logger.exception(excp, exc_info=True)

        app.logger.warning('Backend: WS RPC 已关闭')

        return ws

    app.add_routes(routes)
