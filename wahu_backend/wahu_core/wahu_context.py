from pathlib import Path
from typing import Iterable

from ..aiopixivpy import MaintainedSessionPixivAPI
from ..wahu_config.config_object import WahuConfig
from ..file_tracing import FileTracer
from ..illust_bookmarking import IllustBookmarkDatabase
from ..pixiv_image import PixivImagePool
from ..sqlite_tools.database_ctx_man import DatabaseContextManager
from .wahu_generator_pool import WahuAsyncGeneratorPool
from .repo_db_link import RepoDatabaseLink, RepoEntry


def scan_illust_bookmark_databases(
    p: Path
) -> dict[str, DatabaseContextManager[IllustBookmarkDatabase]]:
    """扫描路径下的所有 .db 文件，并创建对应的 `IllustBookmarkDatabase` 对象"""

    db_paths: list[Path] = []

    for item in p.iterdir():
        if item.is_file() and item.suffix == '.db':
            db_paths.append(item)

    ibds = [
        DatabaseContextManager(IllustBookmarkDatabase(item.stem, item))
        for item in db_paths
    ]

    ibd_dict = {ibd.dd.name: ibd for ibd in ibds}

    return ibd_dict

def create_file_tracers(
    repos: Iterable[RepoEntry]
) -> dict[str, DatabaseContextManager[FileTracer]]:
    """由 名称 到 路径 的字典创建对应的 `FileTracer` 对象"""

    return {
        r.name: DatabaseContextManager(FileTracer(
            r.name, r.path
        ))
        for r in repos
    }


class WahuContext:

    def __init__(self, config: WahuConfig):

        self.config = config

        # PixivAPI
        self.papi: MaintainedSessionPixivAPI = MaintainedSessionPixivAPI(
            config.account_session_path,
            config.refresh_token_path,
            timeout=self.config.api_timeout,
            host=self.config.api_host_ip,
            language=self.config.tag_language,
            ilst_pool_size=self.config.illust_detail_pool_size
        )

        # 插画收藏数据库 Illust_BookmarkDatabase_s
        self.ilst_bmdbs = scan_illust_bookmark_databases(self.config.database_dir)

        # 储存库与数据库的关联
        self.repo_db_link = RepoDatabaseLink(self.config.repos_file)
        self.repo_db_link.load()  # 加载配置文件

        self.ilst_repos = create_file_tracers(self.repo_db_link.repos.values())

        self.repo_db_link.set_repo_and_db_ref(
            repo_ref=self.ilst_repos,
            ibd_ref=self.ilst_bmdbs
        )  # 设置 repo ibd 的引用

        # 图片服务
        self.image_pool = PixivImagePool(
            host=self.config.image_host_ip,
            size=self.config.image_pool_size,
            timeout=self.config.image_timeout
        )

        # 异步生成器池
        self.agenerator_pool = WahuAsyncGeneratorPool(self.config.agenerator_pool_size)

    async def cleanup(self):
        await self.papi.close_session()
        await self.image_pool.close_session()
