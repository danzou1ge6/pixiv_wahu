from typing import Any, Callable, Coroutine, Optional, TypeAlias, TypeVar
from enum import Enum

from .wahu_context import WahuContext



RT = TypeVar('RT')  # Return Type

AsyncFuncWithRet: TypeAlias = Callable[..., Coroutine[Any, Any, RT]]

# WahuMethod 中的中间件的定义
WahuMiddleWare: TypeAlias = Callable[
    [
        AsyncFuncWithRet[RT],
        'WahuArguments',
        WahuContext
    ],
    Coroutine[Any, Any, RT]
]

GenericWahuMethod: TypeAlias = Callable[
    ['WahuArguments', WahuContext],
    Coroutine[Any, Any, RT]
]


class WahuArguments(dict[str, Any]):
    """
    作为 `WahuMethod` 的参数输入
    其实就是个可以直接用 `.` 运算访问键值的字典
    """

    def __getattr__(self, __name: str) -> Any:
        return super().__getitem__(__name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        return super().__setitem__(__name, __value)

