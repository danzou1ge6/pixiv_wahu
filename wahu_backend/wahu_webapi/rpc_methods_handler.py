from ..http_typing import HTTPData, JSONItem
from ..wahu_core import WahuArguments, WahuContext
from ..wahu_methods import WahuMethods
from .obj2jsonizeable import jsonizeablize
from .webapi_exceptions import WahuWebAPIRPCCallError


"""
Wahu POST RPC 协议：
请求格式：
    `method`: str 方法名 e.g. `ilst_bmdb.list_bm`
    `args`: dict 参数字典 e.g.
        {'name': 'danzou1ge6', 'iid': 12345678}
返回格式：
    `type`: 'generator' | 'normal' 分别代表返回生成器还是 JSON 数据
    `return`: 若 `type` 为 `normal` ，为 JSON ，否则为一个 `key` ，用于方法
              `anext` 的 `args` 中
Wahu WebSocket RPC 协议：
请求格式追加 `mcid`: Method Call ID ，用于匹配请求和返回
返回格式追加
    `type` : 'failure' ，标识执行失败
    `mcid`
"""


async def handle_rpc_call(rpc_dict: HTTPData, ctx: WahuContext) -> dict[str, JSONItem]:
    """处理一个rpc请求，返回一个可以 JSON 化的对象"""


    try:

        method_name = rpc_dict['method']
        args_dict = rpc_dict['args']

    except KeyError as e:
        raise WahuWebAPIRPCCallError('参数 method 或 dict 缺失') from e

    if not isinstance(method_name, str):
        raise WahuWebAPIRPCCallError('参数 method 不为 str')

    if not isinstance(args_dict, dict):
        raise WahuWebAPIRPCCallError('参数 args 不为 dict')

    method = WahuMethods.get(method_name)

    if method is None:
        raise WahuWebAPIRPCCallError(f'不存在方法 {method_name}')

    args = WahuArguments(args_dict)

    method_ret = await method(args, ctx)

    # 处理生成器
    if hasattr(method_ret, '__anext__'):
        gen_key = ctx.agenerator_pool.new(method_ret)

        return {'type': 'generator', 'return': gen_key}

    json_ret = jsonizeablize(method_ret)

    return {'type': 'normal', 'return': json_ret}
