from typing import Any
from ..http_typing import HTTPData


class WahuWebAPIError(Exception):
    pass


class WahuJsonizeablizeFail(WahuWebAPIError):
    """当将对象转换为可以 JSON 化的列表或者字典时失败"""

    def __init__(self, target: Any):
        self.target = target

    def __str__(self) -> str:
        return f'对象为 {self.target}'

class WahuBadRPCArgument(WahuWebAPIError):
    """当 `trans_args` 失败时抛出"""
