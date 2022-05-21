import asyncio
from pathlib import Path
from random import randrange
import pytest
import pytest_asyncio

from wahu_backend.aiopixivpy import PixivAPI, MaintainedSessionPixivAPI


@pytest_asyncio.fixture(scope='module')
async def pixiv_api():
    api = PixivAPI()
    yield api
    if hasattr(api, 'session'):
        await api.close_session()


@pytest_asyncio.fixture
async def loggedin_pixiv_api():
    api = MaintainedSessionPixivAPI(
        Path('./dev_stuff/session_info.toml'),
        Path('./dev_stuff/refresh_token.txt')
    )
    async with api.ready:
        yield api
    async with api.ready:
        await api.close_session()

# ------ 测试 Illust APIs


@pytest.fixture(
    params=[
        ('user_illusts', (340139,), {}),
        ('user_bookmarks_illusts', (340139,), {}),
        ('search_illust', ('白发',), {}),
        ('illust_related', (45068168,), {}),
        ('illust_recommended', (), {}),
        ('illust_follow', (), {}),
        ('illust_ranking', (), {'mode': 'day'}),
        ('illust_new', (), {})
    ],
    ids=[
        'user_illusts',
        'user_bookmarks_illusts',
        'search_illust',
        'illust_related',
        'illust_recommended',
        'illust_follow',
        'illust_ranking',
        'illust_new'
    ]
)
def illust_api(request, loggedin_pixiv_api):
    return getattr(loggedin_pixiv_api, request.param[0])(
        *request.param[1], **request.param[2]
    )


@pytest.mark.asyncio
async def test_illust_apis(illust_api):
    ret = await anext(illust_api)
    await asyncio.sleep(randrange(100, 200) / 1000)


# ------ 测试 User APIs
@pytest.fixture(
    params=[
        ('user_following', (340139,), {}),
        ('user_follower', (340139,), {}),
        ('user_related', (340139,), {})
    ],
    ids=[
        'user_following',
        'user_follower',
        'user_related'
    ]
)
def user_api(request, loggedin_pixiv_api):
    return getattr(loggedin_pixiv_api, request.param[0])(
        *request.param[1], **request.param[2]
    )


@pytest.mark.asyncio
async def test_user_apis(user_api):
    ret = await anext(user_api)
    await asyncio.sleep(randrange(100, 200) / 1000)


# ------ 测试其他 APIs
@pytest.mark.asyncio
class TestMiscAPIs:
    @staticmethod
    async def test_user_detail(loggedin_pixiv_api):
        ret = await loggedin_pixiv_api.user_detail(340139)

        assert ret.uid == 340139

    @staticmethod
    async def test_trending_tags_illust(loggedin_pixiv_api):
        ret = await loggedin_pixiv_api.trending_tags_illust()

        assert len(ret) != 0

    @staticmethod
    async def test_illust_comments(loggedin_pixiv_api):
        g = loggedin_pixiv_api.illust_comments(45068168)

        ret = await anext(g)

        assert len(ret) != 0

    @staticmethod
    async def test_illust_detail(loggedin_pixiv_api):
        ret = await loggedin_pixiv_api.illust_detail(45068168)

        assert ret.iid == 45068168

    # 账户管理 APIs 不太好测试，就不测试了（逃
