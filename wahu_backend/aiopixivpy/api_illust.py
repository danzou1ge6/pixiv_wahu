from typing import Any, AsyncGenerator, Optional


from .pixivpy_typing import PixivDuration, HTTPData, PixivRecomMode, PixivRestrict, PixivSearchTarget, PixivSort, URLParams
from .api_base import check_login
from .api_ilst_pool import IllustPoolAPI
from .ap_exceptions import AioPixivPyInvalidReturn
from .datastructure_illust import IllustDetail
from .datastructure_processing import process_pixiv_illust_dict


class IllustPixivAPI(IllustPoolAPI):
    """返回插画的 Pixiv API 集合"""

    def _process_illusts_ret(
            self,
            pr: HTTPData
        ) -> tuple[list[IllustDetail], Optional[str]]:
        """
        对于返回插画详情的 pixiv API 的返回进行处理
        pixiv 返回格式：
            illusts:
                - dict 可用 `process_pixiv_illust_dict` 解析
                - ...
            next_url: None | str
        """

        try:
            illusts_dict = pr['illusts']

            if 'next_url' in pr.keys() and pr['next_url'] is not None:
                assert isinstance(pr['next_url'], str)
                next_url = self.strip_api_host_name(pr['next_url'])
            else:
                next_url = None

            illusts = [process_pixiv_illust_dict(pd) for pd in illusts_dict]  # type: ignore

            return illusts, next_url

        except KeyError or ValueError or TypeError as e:
            raise AioPixivPyInvalidReturn(pr) from e

    def _illusts_generator_factory(
        self,
        url: str,
        **kwds: Any
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """
        返回一个生成器，每次调用这个生成器可以获得插画详情\n
        HTTP 请求是在调用生成器时发起的\n
        生成过程中可能会抛出 `AioPixivPyError` \n
        如果 pixiv 服务器的返回中不包含 `next_url` ，抛出 `StopIteration` \n
        """

        async def gen() -> AsyncGenerator[list[IllustDetail], None]:
            url_in_gen = url
            kwds_in_gen = kwds
            while True:
                self.log_adapter.debug(
                    '生成插画详情: %s %s' % (url_in_gen, kwds_in_gen)
                )

                new_pixiv_ret = await self.get_json(url_in_gen, **kwds_in_gen)

                illusts, next_url = self._process_illusts_ret(new_pixiv_ret)

                # 插画详情缓冲池
                [self._pool_push_illust(ilst) for ilst in illusts]

                yield illusts

                if next_url is None:
                    return

                url_in_gen = next_url
                kwds_in_gen = {}

        return gen()

    @check_login
    def user_illusts(self,
                     user_id: int) -> AsyncGenerator[list[IllustDetail], None]:
        """用户投稿插画"""

        return self._illusts_generator_factory(
            'v1/user/illusts',
            params={
                'user_id': user_id,
                'filter': self._filter_param,
                'type': 'illust'
            }
        )

    @check_login
    def user_bookmarks_illusts(
        self,
        user_id: int,
        restrict: PixivRestrict = 'public',
        offset: int = 0
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """用户收藏插画"""

        return self._illusts_generator_factory(
            'v1/user/bookmarks/illust',
            params={
                'user_id': user_id,
                'restrict': restrict,
                'filter': self._filter_param,
                'offset': offset
            }
        )

    @check_login
    def search_illust(
        self,
        keyword: str,
        search_target: PixivSearchTarget = 'partial_match_for_tags',
        sort: PixivSort = 'date_desc',
        duration: Optional[PixivDuration] = None,
        offset: int = 0
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """搜索插画"""

        params = {
            'word': keyword,
            'search_target': search_target,
            'sort': sort,
            'filter': self._filter_param,
            'offset': offset
        }
        if duration is not None:
            params['duration'] = duration

        return self._illusts_generator_factory('v1/search/illust',
                                               params=params)

    @check_login
    def illust_related(
        self,
        iid: int,
        seed_iids: Optional[list[int]] = None,
        offset: int = 0
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """相关插画"""

        params: URLParams = {
            'illust_id': iid,
            'filter': self._filter_param,
            'offset': offset
        }
        if seed_iids is not None:
            params['seed_illust_ids[]'] = seed_iids

        return self._illusts_generator_factory(
            'v2/illust/related',
            params=params
        )

    @check_login
    def illust_recommended(
        self,
        offset: int=0
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """推荐插画"""

        return self._illusts_generator_factory(
            'v1/illust/recommended',
            params={
                'content_type': 'illust',
                'filter': self._filter_param,
                'include_ranking_label': 'true',
                'offset': offset
            }
        )

    @check_login
    def illust_follow(
        self,
        restrict: PixivRestrict = 'public',
        offset: int=0
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """关注的用户的新作"""

        return self._illusts_generator_factory(
            'v2/illust/follow',
            params={
                'restrict': restrict,
                'offset': offset
            }
        )

    @check_login
    def illust_ranking(
        self,
        mode: PixivRecomMode,
        offset: int=0
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """作品排行"""

        return self._illusts_generator_factory(
            'v1/illust/ranking',
            params={
                'mode': mode,
                'filter': self._filter_param,
                'offset': offset
            }
        )

    @check_login
    def illust_new(self) -> AsyncGenerator[list[IllustDetail], None]:
        """大家的新作"""

        return self._illusts_generator_factory(
            'v1/illust/new',
            params={
                'content_type': 'illust',
                'filter': self._filter_param
            }
        )

