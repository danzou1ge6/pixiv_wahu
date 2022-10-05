import itertools
import sqlite3
from typing import Any, Generic, Iterable, Optional, Type, TypeVar, Union

from .abc import DatabaseRow
from .st_exceptions import (SqliteTableEditingKeyError,
                            SqliteTableEditingMutateIndex)

RT = TypeVar('RT', bound=DatabaseRow)  # row_obj_type for type static checking

class SqliteTableEditor(Generic[RT]):

    __slots__ = ('name', 'heads', 'index_name', 'row_obj_type', 'cursor')

    def __init__(self, name: str, row_obj_type: Type[RT]) -> None:
        """
        实例化一个数据库表编辑器
        - `:param name:` 数据库表的名称
        - `:row_obj_type:` 保存此表每行的类，继承自 `DatabaseRow`
        - `:index_name:` 此表的索引的列名
        """
        self.name = name
        self.heads = row_obj_type.keys

        self.index_name = row_obj_type.index
        self.row_obj_type = row_obj_type

        self.cursor: sqlite3.Cursor

    def bind(self, cursor: sqlite3.Cursor) -> None:
        """
        将此 editor 绑定到数据库指针上
        """
        self.cursor = cursor

    def create(self) -> None:
        """
        创建新表
        """
        column_heads = ','.join((
            f'{k} {self.row_obj_type.adapters[k].store_type.value}'
            if k != self.index_name else
            f'{k} {self.row_obj_type.adapters[k].store_type.value} PRIMARY KEY'
            for k in self.heads))
        self.cursor.execute(f'CREATE TABLE {self.name} '
                            f'({column_heads})')

    def has_created(self):
        """
        是否已经创建表
        """
        return self.cursor.execute(
            "SELECT name FROM sqlite_master "
            f"WHERE type='table' AND name='{self.name}'").fetchone() != None

    def create_if_not(self):
        """
        懒创建
        """
        if not self.has_created():
            self.create()

    def select(self, index_val: Optional[Union[str, int]] = None, **kwds) -> list[RT]:
        """
        使用 SELECT 语句
        - `:param index_val:` 选中的行的 `self.index_name` 列的值
        - `:param kwds:` 如果提供了 ，则使用 `kwds` 作为 `WHERE ` 子句的参数
        """

        if kwds != {}:
            if not set(kwds.keys()).issubset(self.heads):
                raise SqliteTableEditingKeyError(list(kwds.keys()), self.heads)

            query_string = f'SELECT * FROM {self.name} WHERE ' \
                           + ",".join([f"{k}=?" for k in kwds.keys()])
            db_ret = self.cursor.execute(
                query_string,
                tuple((kwds[k] for k in kwds.keys()))
            )

        else:

            if index_val is None:
                query_string = f'SELECT * FROM {self.name}'
                db_ret = self.cursor.execute(query_string).fetchall()
            else:
                query_string = f'SELECT * FROM {self.name} ' \
                    f'WHERE {self.index_name}=?'
                db_ret = self.cursor.execute(query_string,
                                             (index_val, )).fetchall()

        return [
            self.row_obj_type(
                *(self.row_obj_type.adapters[k].deserialized(row[i])
                  for i, k in enumerate(self.heads))) for row in db_ret
        ]

    def select_cols(self,
                    index_val: Optional[Union[str, int]] = None,
                    *,
                    cols: list[str]) -> list[tuple[Any, ...]]:
        """
        使用 SELECT 语句选择若干列
        - `:param index_val:` 选中的行的 `self.index_name` 列的值
        - `:param cols:` 要读取的列
        - `:return:` 转换后的 sqlite 的原始返回
        """

        if cols is not None:
            if not set(cols).issubset(self.heads):
                raise SqliteTableEditingKeyError(cols, self.heads)
        rows_string = ','.join(cols)

        if index_val is None:
            query_string = f'SELECT {rows_string} FROM {self.name}'
            db_ret = self.cursor.execute(query_string).fetchall()
        else:
            query_string = f'SELECT {rows_string} FROM {self.name} ' \
                           f'WHERE {self.index_name}=?'
            db_ret = self.cursor.execute(query_string,
                                         (index_val, )).fetchall()

        return [
            tuple((self.row_obj_type.adapters[k].deserialized(row[i])
                   for i, k in enumerate(cols))) for row in db_ret
        ]

    def has(self, index_val: Union[str, int]) -> bool:
        return self.cursor.execute(
            f'SELECT {self.index_name} FROM {self.name} '
            f'WHERE {self.index_name}=?',
            (index_val,)
        ).fetchone() != None

    def insert(self, rows: Iterable[RT]) -> list[bool]:
        """
        插入新值
        - `:param rows:` 要插入的行
        - `:return result:` `Iterable[bool]` ，如果对应行在数据库中，
                            则值为 `False` ，否则 `True`
        """
        result: list[bool] = []
        for row in rows:
            # 清理旧值
            if self.has(getattr(row, self.index_name)):
                self.delete([getattr(row, self.index_name)])
                result.append(False)
            else:
                result.append(True)

            insert_string = ','.join(itertools.repeat('?', len(self.heads)))
            db_row = (self.row_obj_type.adapters[k].serialized(getattr(row, k))
                      for k in self.heads)

            self.cursor.execute(
                f'INSERT INTO {self.name} VALUES ({insert_string})',
                list(db_row))

        return result

    def delete(
            self,
            index_val_iter: Optional[Iterable[Union[str,
                                                    int]]] = None) -> None:
        """
        删除行
        - `:param index_val:` 要删除的行的索引值；传入 `None` 则清空此表
        """
        if index_val_iter is None:
            self.cursor.execute(f'DELETE FROM {self.name}')
        else:
            self.cursor.executemany(
                f'DELETE FROM {self.name} WHERE {self.index_name}=?',
                zip(index_val_iter))

    def update(self, index_val: Optional[Union[int, str]] = None, **updates) -> None:
        """
        更新行 `WHERE {self.index_name}={index_val}`
        - `:param index_val:` 要更新的行的索引值，必选
        - `:param updates:` 形如 `<key>=<value>` ， `value` 将会被适配器转换
                        `key` 中不能有任何一个是 `self.index_name`
        """
        if self.index_name in updates.keys():
            raise SqliteTableEditingMutateIndex(self.index_name)

        if not set(updates.keys()).issubset(self.heads):
            raise SqliteTableEditingKeyError(list(updates.keys()), self.heads)

        update_str = ','.join((f'{k}=?' for k in updates.keys()))

        if index_val is not None:
            self.cursor.execute(
                f'UPDATE {self.name} SET {update_str} WHERE {self.index_name}=?',
                (*tuple(self.row_obj_type.adapters[k].serialized(updates[k])
                        for k in updates.keys()), index_val))
        else:
            self.cursor.execute(
                f'UPDATE {self.name} SET {update_str}',
                tuple(self.row_obj_type.adapters[k].serialized(updates[k])
                      for k in updates.keys()))
