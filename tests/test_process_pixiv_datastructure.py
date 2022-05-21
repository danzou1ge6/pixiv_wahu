import pytest

from pixiv_dict_examples import illust_dict1, illust_dict2, user_detail_dict

from wahu_backend.aiopixivpy.datastructure_processing import (
    process_pixiv_illust_dict, process_pixiv_user_detail_dict)


@pytest.fixture(params=[illust_dict1, illust_dict2])
def pd(request):
    return request.param


def test_illust(pd):
    illd = process_pixiv_illust_dict(pd)

    assert illd.iid == pd['id']


def test_user():
    pud = process_pixiv_user_detail_dict(user_detail_dict)

    assert pud.uid == user_detail_dict['user']['id']
