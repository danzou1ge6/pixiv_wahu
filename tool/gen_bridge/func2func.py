import ast
import inspect
from typing import Callable

from .structure import PyAnndVar, PyAnnoType, Py2TsConvertionError

def _parse_ast_arg_anno(arg_anno: ast.Name | ast.Subscript | ast.Constant) -> PyAnnoType:
    if isinstance(arg_anno, ast.Name):
        return PyAnnoType(arg_anno.id)

    elif isinstance(arg_anno, ast.Subscript):
        assert isinstance(arg_anno.value, ast.Name)

        if arg_anno.value.id == 'list':
            assert isinstance(arg_anno.slice, (ast.Name, ast.Subscript))
            return PyAnnoType(
                'list',
                args=[_parse_ast_arg_anno(arg_anno.slice)]
            )

        elif arg_anno.value.id == 'tuple':
            assert isinstance(arg_anno.slice, ast.Tuple)
            assert all((isinstance(elt, (ast.Name, ast.Subscript)) for elt in arg_anno.slice.elts))
            return PyAnnoType(
                'tuple',
                args=[_parse_ast_arg_anno(elt) for elt in arg_anno.slice.elts]  # type: ignore
            )

        elif arg_anno.value.id == 'AsyncGenerator':
            assert isinstance(arg_anno.slice, ast.Tuple)
            return PyAnnoType(
                'AsyncGenerator',
                args=[
                    _parse_ast_arg_anno(arg_anno.slice.elts[0]),  # type: ignore
                    _parse_ast_arg_anno(arg_anno.slice.elts[1])  # type: ignore
                ]
            )

        elif arg_anno.value.id == 'Optional':
            return PyAnnoType(
                'Optional',
                args=[_parse_ast_arg_anno(arg_anno.slice)]  # type: ignore
            )

        elif arg_anno.value.id == 'Literal':
            assert isinstance(arg_anno.slice, ast.Tuple)
            return PyAnnoType(
                'Literal',
                args=[
                    PyAnnoType(item.value)  # type: ignore
                    for item in arg_anno.slice.elts
                ]
            )

        elif arg_anno.value.id == 'Union':
            assert isinstance(arg_anno.slice, ast.Tuple)
            return PyAnnoType(
                'Union',
                args=[
                    _parse_ast_arg_anno(item)  # type: ignore
                    for item in arg_anno.slice.elts
                ]
            )

    elif isinstance(arg_anno, ast.Constant):

        if arg_anno.value == None:
            return PyAnnoType('NoneType')

    raise Py2TsConvertionError(f'无法解析 {arg_anno}')



def _parse_func(f: Callable) -> tuple[list[PyAnndVar], PyAnnoType]:
    tree = ast.parse(inspect.cleandoc(inspect.getsource(f)))

    assert isinstance(tree.body[0], (ast.FunctionDef, ast.AsyncFunctionDef))

    args_anno_vars = []
    for arg in tree.body[0].args.args:

        if arg.arg == 'cls':
            continue

        assert isinstance(arg.annotation, (ast.Name, ast.Subscript))
        args_anno_vars.append(PyAnndVar(
            arg.arg,
            _parse_ast_arg_anno(arg.annotation)
        ))

    if isinstance(tree.body[0].returns, ast.Constant) and tree.body[0].returns.value == None:
        ret_anno_tp = PyAnnoType('NoneType')

    else:
        assert isinstance(tree.body[0].returns, (ast.Name, ast.Subscript))
        ret_anno_tp = _parse_ast_arg_anno(tree.body[0].returns)

    return args_anno_vars, ret_anno_tp


def _generage_func_ts_from_anno(
    name: str, args: list[PyAnndVar], ret_tp: PyAnnoType, body, if_async=False) -> str:

    ret = ''
    if if_async:
        ret += 'async '
    ret += f'function {name} '
    ret += '(' + ', '.join((aav.ts for aav in args)) + ')'
    if if_async:
        ret += ' : ' + f'Promise<{ret_tp.ts}>'
    else:
        ret += ' : ' + ret_tp.ts
    ret += ' {\n'

    ret += body

    ret += '}\n'

    return ret

def generate_func_ts(f: Callable, body: str, if_async=False):
    args_anno_vars, ret_anno_tp = _parse_func(f)

    ret = _generage_func_ts_from_anno(
        f.__name__, args_anno_vars, ret_anno_tp, body, if_async=if_async
    )

    return ret


