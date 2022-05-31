from dataclasses import dataclass
from typing import AsyncGenerator

from .datastructure_illust import IllustDetail, IllustTag
from .datastructure_comment import PixivComment
from .datastructure_user import PixivUserDetail
from .datastructure_processing import (process_pixiv_comment_dict,
                                         process_pixiv_illust_dict,
                                         process_pixiv_user_detail_dict)

from .api_base import BasePixivAPI, check_login
from .ap_exceptions import AioPixivPyInvalidReturn
from .datastructure_illust import TrendingTagIllusts


class MiscPixivAPI(BasePixivAPI):
    """一些散装 Pixiv APIs"""

    @check_login
    def illust_comments(
        self,
        iid: int,
        offset: int = 0
    ) -> AsyncGenerator[list[PixivComment], None]:
        """
        插画下的评论
        pixiv 返回格式（伪yaml）:
            total_comments: int
            comments:
                -
                    id: int
                    comment: str
                    date: str 形如 "2020-05-16T01:49:04+09:00"
                    user: 可用 `process_pixiv_user_summery_dict` 解析
                    parent_comment: dict 形如 comments
                - ...
            next_url: str
        """

        async def gen() -> AsyncGenerator[list[PixivComment], None]:
            url = 'v1/illust/comments'
            params = {'illust_id': iid, 'offset': offset}
            while True:
                self.log_adapter.debug(
                    '生成评论: %s %s' % (url, params)
                )

                pr = await self.get_json(url, params=params)

                comments = [
                    process_pixiv_comment_dict(cd)
                    for cd in pr['comments']  # type: ignore
                ]

                if 'next_url' in pr.keys() and pr['next_url'] is not None:
                    assert isinstance(pr['next_url'], str)
                    next_url = self.strip_api_host_name(pr['next_url'])
                else:
                    next_url = None

                yield comments

                if next_url is None:
                    return

                url = next_url
                params = {}

        return gen()

    @check_login
    async def user_detail(self, uid: int) -> PixivUserDetail:
        """
        用户详情
        pixiv 返回格式：
            user: dict
            profile: dict
            profile_publicity: dict
            workspace: dict
        可以使用 `process_pixiv_user_detail_dict 解析
        """
        ret = await self.get_json(
            'v1/user/detail',
            params={
                'user_id': uid,
                'filter': 'for_ios'
            }
        )

        return process_pixiv_user_detail_dict(ret)

    @check_login
    async def trending_tags_illust(self) -> list[TrendingTagIllusts]:
        """
        热门标签
        pixiv 服务器返回格式为（伪yaml）：
            trend_tags:
                -
                    tag: str
                    translated_name: str
                    illust: dict 可用 `process_pixiv_illust_detail` 解析 \n
                - ...

        """

        pixiv_ret = await self.get_json(
            'v1/trending-tags/illust',
            params={'filter': self._filter_param}
        )

        try:
            ret = [
                TrendingTagIllusts(
                    IllustTag(entry['tag'], entry['translated_name']),
                    process_pixiv_illust_dict(entry['illust'])
                )
                for entry in pixiv_ret['trend_tags']  # type: ignore
            ]
            return ret

        except KeyError or ValueError as e:
            raise AioPixivPyInvalidReturn(pixiv_ret) from e
