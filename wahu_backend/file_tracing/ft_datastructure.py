from dataclasses import dataclass
from pathlib import Path

from ..sqlite_tools.abc import DatabaseRow
from ..sqlite_tools.adapters import (IntAdapter, JsonAdapter, PathAdapter,
                                     StrAdapter)

@dataclass(slots=True)
class FileEntryRaw:
    """
    FileTracer 的一条索引
    - :member path: 相对于 `FileTracer.root_path` 的相对路径
    - :member fid: 每个文件的唯一标识符，格式为 `{IllustDetail.iid}-{page_n}`
    """

    path: Path
    fid: str

    def __hash__(self) -> int:
        return hash(self.fid)

    def __eq__(self, __o: 'FileEntryRaw') -> bool:
        return self.fid == __o.fid


class FileEntry(FileEntryRaw, DatabaseRow):
    adapters = {'path': PathAdapter, 'fid': StrAdapter}
    keys = list(adapters.keys())
    index = 'fid'


@dataclass(slots=True)
class FileTracingConfigRaw:
    """
    某一目录下的 FileTracer 的配置
    """

    ftid: int
    name: str
    ignore: list[str]


class FileTracingConfig(FileTracingConfigRaw, DatabaseRow):
    adapters = {
        'ftid': IntAdapter,
        'name': StrAdapter,
        'ignore': JsonAdapter,
    }
    keys = list(adapters.keys())
    index = 'ftid'
