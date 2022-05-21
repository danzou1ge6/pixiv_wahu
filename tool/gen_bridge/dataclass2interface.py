import dataclasses
import types
from typing import Literal, Union

from .structure import PyAnndVar, RAW_TYPES, PyAnnoType


def _parse_typing(tp: type | types.GenericAlias) -> PyAnnoType:
    if tp in RAW_TYPES:
        return PyAnnoType(tp.__name__)  # type: ignore

    if hasattr(tp, '__origin__'):
        if tp.__origin__ == list:  # type: ignore
            return PyAnnoType('list', args=[_parse_typing(tp.__args__[0])])  # type: ignore

        if tp.__origin__ == tuple:  # type: ignore
            return PyAnnoType(
                'tuple',
                args=[_parse_typing(arg_tp) for arg_tp in tp.__args__]  # type: ignore
            )

        if tp.__origin__ == Union:  # type: ignore
            return PyAnnoType(
                'Union',
                args=[_parse_typing(arg_tp) for arg_tp in tp.__args__]  # type: ignore
            )

        if tp.__origin__ == Literal:  # type: ignore
            return PyAnnoType(
                'Literal',
                args=[PyAnnoType(a) for a in tp.__args__]  # type: ignore
            )

    return PyAnnoType(tp.__name__)



def _parse_dataclass_fields(dc: type) -> list[PyAnndVar]:
    fields = dataclasses.fields(dc)
    ret = []

    for f in fields:
        ret.append(PyAnndVar(
            f.name,
            _parse_typing(f.type)
        ))

    return ret


def generate_dataclass_ts(dc: type) -> str:
    anno_fields = _parse_dataclass_fields(dc)

    ret = f'interface {dc.__name__} ''{\n'
    ret += '\n'.join((f'    {var.ts};' for var in anno_fields)) + '\n'
    ret += '}\n'

    return ret


