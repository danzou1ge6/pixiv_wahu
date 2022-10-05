from typing import Any, Callable, Iterable, Optional, Type, TypeVar, Union

from .abc import DatabaseRow
from .st_exceptions import SqliteTableStoreConfigError
from .table_editor import SqliteTableEditor


class SetterGetterProxy:
    def __init__(self, getter: Callable[[str], Any], setter: Callable[[str, Any], None]):
        self.__dict__['setter'] = setter
        self.__dict__['getter'] = getter

    def __getattr__(self, k: str) -> Any:
        return self.getter(k)

    def __setattr__(self, k: str, v: Any) -> None:
        return self.setter(k, v)


RT = TypeVar('RT', bound=DatabaseRow)  # row_obj_type for type static checking


class ConfigStoredinSqlite(SqliteTableEditor[RT]):
    """
    在 sqlite 数据库中储存配置的快捷方式
    - `:property v:` 返回一个 setter 和 getter 的代理对象，在其上可以直接进行 `.` 操作
    """

    __slots__ = ('cfg')

    def __init__(self,
                 row_obj_type: Type[RT],
                 name: str = 'config') -> None:
        super().__init__(name, row_obj_type)


        self.cfg = SetterGetterProxy(self.get, self.set)

    @property
    def empty(self) -> bool:
        return len(self.select()) == 0

    def insert(self, rows: Iterable[RT]) -> list[bool]:
        if not self.empty:
            raise SqliteTableStoreConfigError('配置表中已有数据，拒绝插入新行')

        return super().insert(rows)

    def get(self, key: str) -> Any:
        item = self.select_cols(cols=[key])[0][0]
        return item

    def set(self, key: str, value: Any) -> None:
        self.update(**{key: value})

    def all(self) -> RT:
        return self.select()[0]

    def setall(self, RT) -> None:
        self.delete()
        self.insert([RT])

    @property
    def v(self):
        return self.cfg
