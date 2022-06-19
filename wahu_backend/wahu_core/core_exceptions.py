from typing import Any


class WahuCoreException(Exception):
    pass


class MsgErrorTemplate:

    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

class WahuInitError(WahuCoreException, MsgErrorTemplate):
    """在初始化时出现异常时抛出"""

class WahuMethodArgsKeyError(WahuCoreException):
    """当调用 `Wahu` 方法时 rpc 字典缺少键时抛出"""

    def __init__(self, k: str):
        self.k = k

    def __str__(self) -> str:
        return f'找不到 key {self.k}'

class WahuRuntimeError(WahuCoreException, MsgErrorTemplate):
    """运行时错误"""


class WahuAsyncGeneratorPoolKeyError(WahuCoreException):
    """当 `WahuAsyncGeneratorPool` 中 `KeyError` 时抛出"""

    def __init__(self, k: str):
        self.k = k

    def __str__(self) -> str:
        return f'找不到 key {self.k}'

class WahuCliScriptError(MsgErrorTemplate, WahuCoreException):
    """命令行脚本错误"""
