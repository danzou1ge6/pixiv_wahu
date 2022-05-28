import asyncio
import atexit
from pathlib import Path
from inspect import iscoroutinefunction
from typing import Callable, Coroutine, Iterable

from ..aiopixivpy import MaintainedSessionPixivAPI
from ..file_tracing import FileTracer
from ..illust_bookmarking import IllustBookmarkDatabase
from ..pixiv_image import PixivImagePool
from ..sqlite_tools.database_ctx_man import DatabaseContextManager
from ..wahu_config.config_object import WahuConfig
from .core_exceptions import WahuCliScriptError
from .repo_db_link import RepoDatabaseLink, RepoEntry
from .wahu_generator_pool import WahuAsyncGeneratorPool


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

class WahuCliScript:

    def __init__(
        self,
        path: Path,
        name: str,
        descrip: str,
        init_hook: Callable[['WahuContext'], None],
        cleanup_hook: Callable[['WahuContext'], None]
    ):
        self.path = path
        self.name = name
        self.descrip = descrip
        self.init_hook = init_hook
        self.cleanup_hook = cleanup_hook


def load_cli_scripts(script_dir: Path) -> list[WahuCliScript]:

    cli_scripts = []

    for item in script_dir.iterdir():
        if item.suffix == '.py':

            global_dict = {}

            with open(item, 'r', encoding='utf-8') as wf:
                code = wf.read()
            exec(code, global_dict)

            try:
                name = global_dict['NAME']
                description = global_dict['DESCRIPTION']
            except KeyError:
                raise WahuCliScriptError('缺少元信息 name, description')

            init_hook = global_dict.get('init_hook', None)
            cleanup_hook = global_dict.get('cleanup_hook', None)

            cli_scripts.append(WahuCliScript(
                item,
                name,
                description,
                init_hook,
                cleanup_hook
            ))

    return cli_scripts


class WahuContext:

    cli_scripts: list[WahuCliScript]

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
            timeout=self.config.image_timeout,
            connection_limit=self.config.image_connection_limit,
            num_parallel=self.config.image_num_parallel,
            record_size=self.config.image_download_record_size
        )

        # 异步生成器池
        self.agenerator_pool = WahuAsyncGeneratorPool(self.config.agenerator_pool_size)

        # 命令行脚本 init_hook
        self.cli_scripts = load_cli_scripts(self.config.cli_script_dir)

        for cs in self.cli_scripts:
            cs.init_hook(self)

        atexit.register(self.sync_cleanup)

    async def cleanup(self):
        await self.papi.close_session()
        await self.image_pool.close_session()

    def sync_cleanup(self):

        for cs in self.cli_scripts:
            cs.cleanup_hook(self)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.cleanup())
