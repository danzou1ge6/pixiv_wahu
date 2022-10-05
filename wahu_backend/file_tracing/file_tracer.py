import re
import sqlite3
from pathlib import Path
from random import getrandbits
from typing import Iterable, Optional

from ..sqlite_tools.abc import DependingDatabase
from ..sqlite_tools import ConfigStoredinSqlite, SqliteTableEditor
from .ft_datastructure import FileEntry, FileTracingConfig
from .log_adapter import FileTracerLoggingAdapter
from .logger import logger

# 默认要忽略的文件
DEFAULT_IGNORE_LIST = [r'.+\.aria2', r'index.db', r'index.db-journal']


class FileTracerBase(DependingDatabase):
    """
    `FileTracer` 的基类
    - `:attr name:` 用于在应用中标识此目录
    - `:attr root_path:` 要跟踪的文件所在根目录
    - `:attr indexed_te:` 已经索引的文件的索引
    - `:attr cached_te:` 缓存的文件的索引
            如果文件存在，调用 `update_index` 时会被移入 `indexed`
    - `:attr config_table_editor:` 保存配置的 sqlite 表
    - `:attr config:` `config_table_editor.get / set` 的简写
    路径以相对路径的形式储存在数据库中
    """

    def get_default_config(self) -> FileTracingConfig:
        """返回当前实例的默认配置"""

        config = FileTracingConfig(
            getrandbits(16),
            self.name,
            DEFAULT_IGNORE_LIST)
        return config


    indexed_te :SqliteTableEditor[FileEntry] = SqliteTableEditor('indexed', FileEntry)
    cached_te :SqliteTableEditor[FileEntry] = SqliteTableEditor('cached', FileEntry)

    config_table_editor: ConfigStoredinSqlite[FileTracingConfig] = \
        ConfigStoredinSqlite(
            FileTracingConfig,
            name='config'
    )
    
    __slots__ = (
        'log_adapter', 'name', 'root_path', 'index_path', 'config',
        'index_con'
    )

    def __init__(self, name: str, root_path: Path):

        self.log_adapter = FileTracerLoggingAdapter(name, logger)

        if not root_path.exists():
            root_path.mkdir(parents=True)  # 任何找不到的父目录都会被创建

            self.log_adapter.warning('init: 根目录 %s 不存在，自动创建' % root_path)

        self.name = name
        self.root_path = root_path

        self.index_path = root_path / 'index.db'


        self.config = self.config_table_editor.v  # 这样就能使用简写 config.ignore

        self.log_adapter.info('init: 名称=%s 根目录=%s' % (name, root_path))

        self.index_con: sqlite3.Connection

    def connect(self) -> None:
        """连接数据库，并创建所有表"""

        self.index_con = sqlite3.connect(self.index_path)
        index_cur = self.index_con.cursor()

        self.indexed_te.bind(index_cur)
        self.indexed_te.create_if_not()

        self.cached_te.bind(index_cur)
        self.cached_te.create_if_not()

        self.config_table_editor.bind(index_cur)
        self.config_table_editor.create_if_not()

        if self.config_table_editor.empty:
            self.config_table_editor.insert([self.get_default_config()])

    def close(self, commit: bool = True) -> None:
        """关闭数据库连接"""

        if commit:
            self.index_con.commit()
        self.index_con.close()


class FileTracerIndexingMixin(FileTracerBase):

    def add_cache(self, entries: list[FileEntry]) -> None:
        """将一组 FileEntry 加入数据库"""

        self.cached_te.insert(entries)

        self.log_adapter.debug('add_cache: 添加缓存 %s' % entries)
        self.log_adapter.info('add_cache: 添加了 %s 条缓存' % len(entries))

    def empty_cache(self) -> None:
        """清空数据库的 cache 表"""
        self.cached_te.delete()

        self.log_adapter.info('empty_cache: 清理缓存')

    def update_index(self) -> list[FileEntry]:
        """
        根据本地文件存在情况，将 cached 表中的项移入 indexed 表
        """
        cached_entries = self.cached_te.select()

        new_entries = list(
            filter(lambda ce: (self.root_path / ce.path).exists(),
                   cached_entries))

        self.log_adapter.debug('update_index: 添加索引 %s' % new_entries)
        self.log_adapter.info('update_index: 添加了 %s 条索引' % len(new_entries))

        self.indexed_te.insert(new_entries)
        self.cached_te.delete((ne.fid for ne in new_entries))

        return new_entries

    def remove_index(self, fids: Iterable[str]) -> None:
        """
        根据 fid 删除若干索引
        """
        self.indexed_te.delete(fids)

        self.log_adapter.info('remove_index: 删除了索引 %s' % fids)

    def checkout(self, fid: str) -> Optional[Path]:
        """
        从 indexed 表检出
        :param fid: 文件唯一标识。如果请求的 `fid` 不在 indexed 表中，返回None
        """

        ie = self.indexed_te.select(fid)

        if ie == []:
            self.log_adapter.debug('checkout: 文件 fid=%s 不在索引中' % fid)
            return None
        else:
            self.log_adapter.debug('checkout: 检出文件 %s' % ie[0])
            return self.root_path / ie[0].path

    def all_index(self) -> list[FileEntry]:
        """检出所有 indexed 表中的内容. FileEntry.path 为相对路径"""
        return self.indexed_te.select()

    def all_cache(self) -> list[FileEntry]:
        return self.cached_te.select()


class FileTracerConfigMixin(FileTracerBase):

    def get_config(self) -> FileTracingConfig:
        """从 index.db 加载配置，并返回"""
        config = self.config_table_editor.select()[0]

        self.log_adapter.debug('load_config: 加载配置 %s' % config)

        return config


class FileTracerValidationMixin(FileTracerBase):

    def scan(self) -> list[Path]:
        """扫描本地文件，除去 `ignore_list` 中的项后存入 `self.file_list`"""
        raw_file_list = list(self.root_path.iterdir())  # 相对路径

        ignore_list = self.config.ignore

        self.log_adapter.debug('scan: 忽略 %s' % ignore_list)

        file_list = list(
            filter(
                lambda p: all(
                    (re.match(ig, p.name) is None for ig in ignore_list)),
                raw_file_list))

        self.log_adapter.info('scan: 根目录下有 %s 个文件' % len(file_list))

        return file_list

    def validate_index(self) -> list[FileEntry]:
        """
        检查 indexed 中的所有文件是否存在，返回不存在的项
        :return: `FileEntry.path` 与 `add_cache` 时保持一致，因为从数据库读出
        """

        indexed_entries = self.indexed_te.select()
        invalid_indexs = list(
            filter(lambda ie: not (self.root_path / ie.path).exists(),
                   indexed_entries))

        self.log_adapter.debug('validate_index: 不存在的索引 %s' % invalid_indexs)
        self.log_adapter.info(
            'validate_index: 不存在的索引有 %s 条' % len(invalid_indexs))

        return invalid_indexs

    def validate_files(self) -> list[Path]:
        """
        检查根目录中的所有文件是否都在 indexed 表中，返回不在的项
        :return: 添加了 `self.root_path` 的路径
        """

        file_list = self.scan()

        indexed_entries = self.indexed_te.select()
        indexed_pnames = [ie.path.name for ie in indexed_entries]
        invalid_paths = list(
            filter(lambda p: p.name not in indexed_pnames, file_list))

        self.log_adapter.debug('validate_files: 未被索引的文件 %s' % invalid_paths)
        self.log_adapter.info('未被索引的文件有 %s 条' % len(invalid_paths))

        return [p for p in invalid_paths]


class FileTracer(FileTracerConfigMixin, FileTracerIndexingMixin, FileTracerValidationMixin):
    """
    对于某个目录下的文件进行索引；处于效率考量（以及懒）不进行递归搜索
    """


__all__ = ['FileTracer']
