import dataclasses

import pytest
import pytest_asyncio
from wahu_backend.aiopixivpy.datastructure_illust import IllustTag, PixivUserSummery

from pixiv_dict_examples import illust_dict1, illust_dict2

from wahu_backend.aiopixivpy import IllustDetail
from wahu_backend.aiopixivpy.datastructure_processing import process_pixiv_illust_dict
from wahu_backend.illust_bookmarking import IllustBookmarkDatabase

illust_detail1 = process_pixiv_illust_dict(illust_dict1)
illust_detail2 = process_pixiv_illust_dict(illust_dict2)


@pytest.fixture(scope='class')
def ibd():
    ibd = IllustBookmarkDatabase('test', ':memory:')
    ibd.connect()
    yield ibd
    ibd.close()


async def get_detail(iid):
    if iid == illust_detail1.iid:
        return illust_detail1
    elif iid == illust_detail2.iid:
        return illust_detail2
    else:
        raise RuntimeError()


@pytest.mark.asyncio
class TestSet:
    @staticmethod
    async def test_add(ibd):
        f1, f2 = await ibd.set_bookmark(illust_detail1.iid, [0], get_detail=get_detail)
        f3, f4 = await ibd.set_bookmark(illust_detail2.iid, [0], get_detail=get_detail)

        assert f1 == f2 == f3 == f4 == True

        assert ibd.bookmarks_te.has(illust_detail1.iid)
        assert ibd.bookmarks_te.has(illust_detail2.iid)

        assert ibd.bookmarks_te.select(
            illust_detail1.iid)[0].pages == [0]

    @staticmethod
    async def test_del(ibd):
        f1, f2 = await ibd.set_bookmark(illust_detail1.iid, [])

        assert f1 == f2 == True

        assert not ibd.bookmarks_te.has(illust_detail1.iid)
        assert not ibd.bookmarks_te.has(illust_detail1.iid)

    @staticmethod
    async def test_del_none(ibd):
        f1, f2 = await ibd.set_bookmark(0, [])

        assert f1 == f2 == False

    @staticmethod
    async def test_alter(ibd):
        f1, f2 = await ibd.set_bookmark(illust_detail2.iid, [0, 1])

        assert f1 == f2 == False

        assert ibd.bookmarks_te.select(
            illust_detail2.iid)[0].pages == [0, 1]


async def get_detail_mod(iid):
    if iid == illust_detail1.iid:
        modified_ilstd1 = IllustDetail(*dataclasses.astuple(illust_detail1))
        modified_ilstd1.title = 'Kotori!Kotori!'
        # 因为 astuple 递归地对所有子 dataclass 进行转换，所以需要再转回来
        modified_ilstd1.user = PixivUserSummery(
            *modified_ilstd1.user)  # type: ignore
        modified_ilstd1.tags = [
            IllustTag(n, t) for n, t in modified_ilstd1.tags]  # type: ignore
        return modified_ilstd1
    elif iid == illust_detail2.iid:
        return illust_detail2
    else:
        raise RuntimeError()


@pytest_asyncio.fixture
async def init_with_detail(ibd):
    await ibd.set_bookmark(illust_detail1.iid, [0], get_detail=get_detail)
    await ibd.set_bookmark(illust_detail2.iid, [0], get_detail=get_detail)


@pytest_asyncio.fixture
async def init_without_detail(ibd):
    await ibd.set_bookmark(illust_detail1.iid, [0], get_detail=None)
    await ibd.set_bookmark(illust_detail2.iid, [0], get_detail=None)


@pytest.mark.asyncio
@pytest.mark.usefixtures('init_without_detail')
class TestUpdateDetail:

    @staticmethod
    async def test_update(ibd):
        assert not ibd.illusts_te.has(illust_detail1.iid)
        assert not ibd.illusts_te.has(illust_detail2.iid)

        await ibd.update_detail(get_detail=get_detail)

        assert ibd.illusts_te.has(illust_detail1.iid)
        assert ibd.illusts_te.has(illust_detail2.iid)

    @staticmethod
    async def test_update_all(ibd):
        await ibd.update_detail(get_detail=get_detail_mod, update_all=True)

        assert ibd.illusts_te.select(illust_detail1.iid)[
            0].title == 'Kotori!Kotori!'


@pytest.mark.asyncio
@pytest.mark.usefixtures('init_with_detail')
class TestQuery:

    @staticmethod
    async def test_query_detail(ibd):
        ret = ibd.query_detail(illust_detail1.iid)

        assert ret.iid == illust_detail1.iid

    @staticmethod
    async def test_query_detail_none(ibd):
        ret = ibd.query_detail(0)

        assert ret == None

    @staticmethod
    async def test_query_bookmark(ibd):
        ret = ibd.query_bookmark(illust_detail2.iid)

        assert ret.iid == illust_detail2.iid
        assert ret.pages == [0]

    @staticmethod
    async def test_query_bookmark_none(ibd):
        ret = ibd.query_bookmark(0)

        assert ret == None


def get_user_illusts(uid):
    if uid != 123:
        raise RuntimeError()

    async def g():
        yield [illust_detail1]
        yield [illust_detail2]

    return g()


def get_user_bookmarks(uid):
    if uid != 123:
        raise RuntimeError()

    async def g():
        yield [illust_detail1]
        yield [illust_detail2]

    return g()


@pytest.mark.usefixtures('init_with_detail')
class TestFuzzyQuery:

    @staticmethod
    def test_query_title(ibd):
        ret = ibd.query_title('ド')
        assert ret[0].iid == 63343772

    @staticmethod
    def test_query_caption(ibd):
        ret = ibd.query_caption('happy')
        assert ret[0].iid == 63343772

    @staticmethod
    def test_query_username(ibd):
        ret = ibd.query_username('maruma')
        assert ret[0].iid == 63343772

    @staticmethod
    def test_query_tag(ibd):
        ret = ibd.query_tag('Kudryavka')
        assert ret[0].iid == 63343772

    @staticmethod
    def test_query_uid(ibd):
        ret = ibd.query_uid(12501110)
        assert ret[0] == 63343772
