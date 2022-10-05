from typing import Any, Type

from .adapters import SqliteAdapter

class DatabaseRow:
    """
    数据库中的一行
    - :member keys: 这行的所有表头
    - :member adapters: `keys` 作为键值的字典，用于转换类型以存入/读出数据库
    - :member index: 在数据库中作为索引的键值
    """
    keys: list[str]
    adapters: dict[str, Type[SqliteAdapter[Any, Any]]]
    index: str

    __slots__ = ()

    def __init__(self, *args: Any):
        raise NotImplementedError

class DependingDatabase:
    """需要数据库连接的抽象基类"""
    __slots__ = ()

    def connect(self) -> None:
        raise NotImplementedError

    def close(self, commit: bool) -> None:
        raise NotImplementedError
