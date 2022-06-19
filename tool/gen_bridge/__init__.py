from .func2func import _parse_func, _generage_func_ts_from_anno
from .dataclass2interface import generate_dataclass_ts, _parse_typing
from wahu_backend.wahu_methods import WahuMethods
from wahu_backend.exposed_datastructure import exports, exports_type
from wahu_backend.wahu_core.wahu_method import WahuMethod
import sys
sys.path.append('./')

"""
将后端的 dataclass 定义 和 WahuMethods 的类型标注转换为 typescript
"""


def gen_type_alise():
    ret = ''

    ret += 'export type Path = string\n'
    ret += 'export type datetime = string\n'

    for tp_name in exports_type.keys():
        anno_tp = _parse_typing(exports_type[tp_name])
        ret += f'export type {tp_name} = {anno_tp.ts}\n'

    return ret + '\n'


def gen_interfaces():
    ret = ''

    for dc in exports:
        ret += generate_dataclass_ts(dc) + '\n'

    ret += 'export type {' + ', '.join((
        dc.__name__ for dc in exports)) + '}\n\n'
    return ret


def gen_methods():

    ret = ''

    for name in dir(WahuMethods):

        if name.startswith('__') or name in {'anext', 'get', 'wexe'}:
            continue

        m = getattr(WahuMethods, name)

        assert m is not None

        args_vars, ret_tp = _parse_func(m.f)
        args_vars = args_vars[1:]  # 扔掉参数 ctx

        body = f"    return await wahuRPCCall('{m.name}', "
        body += "[" + \
            ', '.join((var.name for var in args_vars)) + '])'
        body += f'as {ret_tp.ts}'

        ret += 'export ' + _generage_func_ts_from_anno(
            m.name, args_vars, ret_tp, body, if_async=True
        ) + '\n'

    return ret


def gen_ts():
    ret = 'import {wahuRPCCall} from "./client"\n\n'
    ret += gen_type_alise()
    ret += gen_interfaces()
    ret += gen_methods()

    with open('./src/plugins/wahuBridge/methods.ts', 'w', encoding='utf=8') as wf:
        wf.write(ret)


if __name__ == '__main__':
    gen_ts()
