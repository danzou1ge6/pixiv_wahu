from typing import Any, AsyncGenerator, Optional

from .ap_exceptions import AioPixivPyInvalidReturn
from .api_base import check_login
from .api_ilst_pool import IllustPoolAPI
from .datastructure_processing import (process_pixiv_illust_dict,
                                       process_pixiv_user_summery_dict)
from .datastructure_user import PixivUserPreview
from .pixivpy_typing import PixivDuration, PixivRestrict, PixivSort


class UserPixivAPI(IllustPoolAPI):
    """
    返回用户的 Pixiv API 集合
    """


    def _process_users_ret(
            self, pr: dict) -> tuple[list[PixivUserPreview], Optional[str]]:
        """
        对于返回用户预览（ `PixivUserPreview` ）的 pixiv API 的返回进行处理
        pixiv 返回格式（伪yaml）：
            user_previews:
                -
                    user: dict 可以用 `process_pixiv_user_summery_dict` 解析 \n
                    illusts:
                        - dict 可以用 `process_pixiv_illust_dict` 解析 \n
                        - ... \n
                - ... \n
            next_url: None | str
        """
        try:
            up_list = pr['user_previews']


            if 'next_url' in pr.keys() and pr['next_url'] is not None:
                next_url = self.strip_api_host_name(pr['next_url'])
            else:
                next_url = None

            user_previews = [
                PixivUserPreview(
                    process_pixiv_user_summery_dict(up['user']),
                    [process_pixiv_illust_dict(illst) for illst in up['illusts']]
                )
                for up in up_list
            ]
            return user_previews, next_url

        except KeyError or ValueError as e:
            raise AioPixivPyInvalidReturn(pr) from e

    def _userpreviews_generator_factory(
            self, url: str,
            **kwds: Any
        ) -> AsyncGenerator[list[PixivUserPreview], None]:
        """
        返回一个生成器，每次调用这个生成器可以获得用户预览 \n
        HTTP 请求是在调用生成器时发起的 \n
        生成过程中可能会抛出 `AioPixivPyError` \n
        如果 pixiv 服务器的返回中不包含 `next_url` ，抛出 `StopIteration` \n
        """

        async def gen() -> AsyncGenerator[list[PixivUserPreview], None]:
            url_in_gen = url
            kwds_in_gen = kwds
            while True:
                self.log_adapter.debug(
                    '生成用户预览: %s %s' % (url_in_gen, kwds_in_gen)
                )

                new_pixiv_ret = await self.get_json(url_in_gen, **kwds_in_gen)

                user_previews, next_url = self._process_users_ret(new_pixiv_ret)

                [[self._pool_push_illust(ilst) for ilst in prev.illusts]
                 for prev in user_previews]

                yield user_previews

                if next_url is None:
                    return

                url_in_gen = next_url
                kwds_in_gen = {}

        return gen()

    @check_login
    def user_following(
        self,
        uid: int,
        restrict: PixivRestrict='public',
        offset: int=0
    ) -> AsyncGenerator[list[PixivUserPreview], None]:
        """用户 `uid` 关注的用户"""

        return self._userpreviews_generator_factory(
            'v1/user/following',
            params={
                'user_id': uid,
                'restrict': restrict,
                'filter': self._filter_param,
                'offset': offset
            }
        )

    @check_login
    def user_follower(
        self,
        uid: int,
        restrict: PixivRestrict='public',
        offset: int=0
    ) -> AsyncGenerator[list[PixivUserPreview], None]:
        """关注用户 `uid` 的用户"""

        return self._userpreviews_generator_factory(
            'v1/user/follower',
            params={
                'user_id': uid,
                'restrict': restrict,
                'filter': self._filter_param,
                'offset': offset
            }
        )

    @check_login
    def user_related(
        self,
        seed_uid: int,
        offset: int=0
    ) -> AsyncGenerator[list[PixivUserPreview], None]:
        """相关用户"""

        return self._userpreviews_generator_factory(
            'v1/user/related',
            params={
                'filter': self._filter_param,
                'seed_user_id': seed_uid,
                'offset': offset
            }
        )

    @check_login
    def search_user(
        self,
        keyword: str,
        sort: PixivSort='date_desc',
        duration: Optional[PixivDuration]=None,
        offset: int=0
    ) -> AsyncGenerator[list[PixivUserPreview], None]:
        """搜索用户"""

        params={
            'word': keyword,
            'sort': sort,
            'filter': self._filter_param,
            'offset': offset
        }
        if duration is not None:
            params['duration'] = duration

        return self._userpreviews_generator_factory(
            'v1/search/user',
            params=params
        )
