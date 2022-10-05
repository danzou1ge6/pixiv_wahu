import json
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar, Union

from enum import Enum

"""
这个模块定义了 sqlite 适配器，用于将 object 转换为可以储存在 sqlite 数据库中的数据类型
- `:class SqliteAdapter:` 抽象基类
- `:class NoneAdapterMethods:` 不进行转换
以及其他一些常用适配器
"""


class SqliteStoreType(Enum):
    """
    可以用于在 sqlite 中储存的数据类型
    """
    TEXT = 'TEXT'
    INTEGER = 'INTEGER'


TO = TypeVar('TO')  # Type Object
TS = TypeVar('TS')  # Type Serialized


class SqliteAdapter(Generic[TO, TS]):
    """
    - `:member store_type:` 储存在 sqlite 数据库里的数据类型
    """
    store_type: SqliteStoreType

    @staticmethod
    def serialized(_: TO) -> TS:
        """将源类型转为目标类型，即 `store_type`"""
        raise NotImplementedError

    @staticmethod
    def deserialized(_: TS) -> TO:
        """将目标类型转为原类型"""
        raise NotImplemented


class NoneAdapterMethods:

    @staticmethod
    def serialized(inp: Any) -> Any:
        return inp

    @staticmethod
    def deserialized(inp: Any) -> Any:
        return inp


class IntAdapter(NoneAdapterMethods, SqliteAdapter[int, int]):
    store_type = SqliteStoreType.INTEGER


class StrAdapter(NoneAdapterMethods, SqliteAdapter[int, int]):
    store_type = SqliteStoreType.TEXT


class BoolAdapter(SqliteAdapter[bool, int]):
    store_type = SqliteStoreType.INTEGER

    @staticmethod
    def serialized(b: bool) -> int:
        return 1 if b else 0

    @staticmethod
    def deserialized(integer: int) -> bool:
        return bool(integer)


class JsonAdapter(SqliteAdapter[Union[list, dict], str]):
    store_type = SqliteStoreType.TEXT

    @staticmethod
    def serialized(dictionary: Union[list, dict]) -> str:
        return json.dumps(dictionary, ensure_ascii=False)

    @staticmethod
    def deserialized(string: str) -> Union[list, dict]:
        return json.loads(string)


class PathAdapter(SqliteAdapter[Path, str]):
    store_type = SqliteStoreType.TEXT

    @staticmethod
    def serialized(p: Path) -> str:
        return str(p)

    @staticmethod
    def deserialized(s: str) -> Path:
        return Path(s)


class CustomAdapterMeta(type):

    def __new__(cls, name: str, store_type: SqliteStoreType,
                serializer: Callable[[TO], TS],
                deserializer: Callable[[TS], TO]) -> type:
        return type(
            name, 
            (SqliteAdapter, ), 
            {
                'serialized': staticmethod(serializer),
                'deserialized': staticmethod(deserializer),
                'store_type': store_type
            }
        )
