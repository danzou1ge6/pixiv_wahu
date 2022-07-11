import sys
sys.path.append('./')
from pathlib import Path
from wahu_backend.sqlite_tools.database_ctx_man import DatabaseContextManager
from tempfile import TemporaryDirectory
import pytest_asyncio
from wahu_backend.wahu_config.config_object import WahuConfig
from wahu_backend.wahu_config.load_config import load_config
from wahu_backend.illust_bookmarking.illust_bookmark_database import IllustBookmarkDatabase
from wahu_backend.wahu_core.wahu_context import WahuContext
import asyncio
import pytest
from wahu_backend.aiopixivpy.datastructure_processing import (
    process_pixiv_illust_dict, process_pixiv_user_detail_dict,
    process_pixiv_user_summery_dict)
from wahu_backend.aiopixivpy.datastructure_user import PixivUserPreview
from pixiv_dict_examples import (illust_dict1, illust_dict2, user_detail_dict,
                                 user_preview_dict)
import pyximport
pyximport.install()


@pytest.fixture(params=[illust_dict1, illust_dict2], scope='session')
def illust_detail(request):
    return process_pixiv_illust_dict(request.param)


@pytest.fixture(scope='module')
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture
def user_detail():
    return process_pixiv_user_detail_dict(user_detail_dict)


@pytest.fixture
def user_preview():
    up = user_preview_dict
    return PixivUserPreview(
        process_pixiv_user_summery_dict(up['user']),
        [process_pixiv_illust_dict(illst) for illst in up['illusts']]
    )


@pytest.fixture(scope='module')
def tmp_dir_path():
    with TemporaryDirectory() as td:
        yield Path(td)
    return


@pytest_asyncio.fixture(scope='module')
async def wahu_ctx():
    cfg = load_config(Path('dev_stuff/dev_conf.toml'))
    ctx = WahuContext(cfg)

    return ctx
