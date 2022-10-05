import dataclasses
from typing import TYPE_CHECKING, Iterable
import toml
from pathlib import Path

from ..wahu_core.core_exceptions import WahuInitError

if TYPE_CHECKING:
    from ..file_tracing import FileTracer
    from ..sqlite_tools.database_ctx_man import DatabaseContextManager
    from ..illust_bookmarking import IllustBookmarkDatabase
    from ..wahu_config.load_config import WPath


@dataclasses.dataclass(slots=True)
class RepoEntry:
    path: Path
    name: str
    linked_databases: list[str]

    def as_dict(self):
        return {
            'path': str(self.path),
            'name': self.name,
            'linked_databases': self.linked_databases
        }



def calc_repo_for_databases(repos: Iterable[RepoEntry]
) -> dict[str, list[str]]:

    ret: dict[str, list[str]] = {}

    for r in repos:
        for db in r.linked_databases:
            if db in ret.keys():
                ret[db].append(r.name)
            else:
                ret[db] = [r.name]

    return ret

class RepoDatabaseLink:
    """
    跟踪储存库与数据库之间的联系
    - `:attr repos:` 储存库的配置信息，所有量以此为基础求得
    - `:attr rfd:` 数据库名到储存库名的映射
    - `:attr dfr:` 储存库名到数据库名的映射
    """

    def __init__(self, cfg_path: Path, wpath: 'WPath'):

        self.cfg_path = cfg_path
        self.wpath = wpath

        self.repos: dict[str, RepoEntry]

    def set_repo_and_db_ref(
        self,
        repo_ref: dict[str, 'DatabaseContextManager[FileTracer]'],
        ibd_ref: dict[str, 'DatabaseContextManager[IllustBookmarkDatabase]']
    ) -> None:

        self.repo_ref = repo_ref
        self.ibd_ref = ibd_ref

    def rfd(self, name: str) -> list['DatabaseContextManager[FileTracer]']:
        """
        数据库 到 储存库 的映射；不存在的储存库将被忽略；没有则返回空列表
        """
        if name in self.rname_for_db.keys():
            return [self.repo_ref[n]
                    for n in self.rname_for_db[name] if n in self.repo_ref.keys()]
        else:
            return []

    def dfr(self, name: str) -> list['DatabaseContextManager[IllustBookmarkDatabase]']:
        """
        储存库 到 数据库 的映射；不存在的数据库将被忽略；没有将返回空列表
        """

        r = self.repos[name]
        return [self.ibd_ref[n] for n in r.linked_databases if n in self.ibd_ref.keys()]

    def load(self) -> None:

        if not self.cfg_path.exists():
            repos = []

        else:
            d = toml.load(self.cfg_path)

            try:
                repos = [
                    RepoEntry(self.wpath(r['path']), r['name'], r['linked_databases'])
                    for r in d['repos']
                ]
                if not all((isinstance(r.linked_databases, list) for r in repos)):
                    raise ValueError('linked_databases 应为 list')
            except KeyError or TypeError as e:
                raise WahuInitError('不合法的 repo 列表文件') from e

        self.repos = {r.name: r for r in repos}
        self.update_rfd()

    def update_rfd(self):
        """
        更新 数据库名 到 储存库名 的映射
        应在每次更改 `self.repos` 后调用
        """

        self.rname_for_db = calc_repo_for_databases(self.repos.values())

    def set_repo_linked_db(self, name: str, dbs: list[str]):
        """设置储存库连接的数据库，数据库可以不存在"""

        self.repos[name].linked_databases = dbs
        self.update_rfd()
        self.write()

    def write(self) -> None:

        d = {
            'repos': [
                r.as_dict()
                for r in self.repos.values()
            ]
        }

        with open(self.cfg_path, 'w', encoding='utf-8') as wf:
            toml.dump(d, wf)


