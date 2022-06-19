import inspect
from typing import Any, Iterable, Union, Literal
from types import NoneType
import dataclasses

from ..wahu_core import WahuArguments
from .webapi_exceptions import WahuBadRPCArgument
from ..http_typing import JSONItem


def trans_json(data: JSONItem, model: type) -> Any:
    """
    将 JSON 数据 转换为 list 和 Dataclass
    """

    if not hasattr(model, '__args__'):

        if dataclasses.is_dataclass(model):
            # 处理 Dataclass

            assert isinstance(data, dict)

            fields = dataclasses.fields(model)

            init_kwds = {
                fie.name: trans_json(data[fie.name], fie.type)
                for fie in fields
            }

            return model(**init_kwds)

        elif model is Any:
            # 不进行转换

            return data

        else:
            return model(data)

    else:
        m_args = model.__args__  # type: ignore
        m_origin = model.__origin__  # type: ignore

        if m_origin is list or m_origin is tuple:
            # 处理 list 和 tuple

            assert isinstance(data, (list, tuple))

            list_args_model = m_args[0]

            return [
                trans_json(d, list_args_model)
                for d in data
            ]

        elif m_origin is Union:
            # 仅支持 Union[X, None]， 即 Optional[X]

            assert len(m_args) == 2 and m_args[1] is NoneType

            if data is None:
                return None
            else:
                return trans_json(data, m_args[0])

        elif m_origin is Literal:
            # 处理字面值

            assert isinstance(data, str)

            if data not in m_args:
                raise WahuBadRPCArgument(f'invalid Literal: {data} not in {m_args}')

            return data

        else:
            raise WahuBadRPCArgument(f'invalid model: {model}')


def trans_args(paras: Iterable[inspect.Parameter], args: list[JSONItem]) -> WahuArguments:
    """
    将 JSON RPC 调用的参数列表转换为 WahuArguments
    """

    args_transed = {
        para.name: trans_json(args[i], para.annotation)
        for i, para in enumerate(paras)
    }

    return WahuArguments(args_transed)
