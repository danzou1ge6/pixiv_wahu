from typing import Any, Optional

from .pixivpy_typing import PixivRestrict
from .api_base import BasePixivAPI, check_login


class AccountControlPixivAPI(BasePixivAPI):
    """账户控制相关 API"""

    @check_login
    async def illust_bookmark_add(
        self,
        iid: int,
        restrict: PixivRestrict='public',
        tags: Optional[list[str]]=None
    ) -> None:
        """
        添加收藏插画\n
        如果成功，pixiv 服务器会返回一个空 JSON 字符串 `{}`；
        否则会返回 404 错误，以及一个
            {'error': {
                  'user_message': '不正なリクエストです。',
                  'message': '',
                  'reason': '',
                  'user_message_details': {}
              }}
        的字典
        """

        data: dict[str, Any]={
            'illust_id': iid,
            'restrict': restrict
        }
        if tags is not None:
            data['tags[]'] = ' '.join(str(tag) for tag in tags)

        self.log_adapter.info(
            'illust_bookmark_add: 尝试添加插画收藏 %s %s'
            % (iid, restrict)
        )

        await self.post_json('v2/illust/bookmark/add', data=data)

        # 处理插画详情池
        if iid in self.ilst_pool.keys():
            self.ilst_pool[iid].is_bookmarked = True

    @check_login
    async def illust_bookmark_delete(self, iid: int) -> None:
        """删除收藏插画"""

        self.log_adapter.info('illust_bookmark_delete: 尝试删除插画收藏 %s'
                              % iid)

        await self.post_json(
            'v1/illust/bookmark/delete', data={'illust_id': iid}
        )

        # 处理插画详情池
        if iid in self.ilst_pool.keys():
            self.ilst_pool[iid].is_bookmarked = False

    @check_login
    async def user_follow_add(
        self,
        uid: int,
        restrict: PixivRestrict='public'
    ) -> None:
        """关注用户"""

        self.log_adapter.info('user_follow_add: 尝试关注用户 %s'
                              % uid)

        await self.post_json(
            'v1/user/follow/add',
            data={'user_id': uid, 'restrict': restrict}
        )

    @check_login
    async def user_follow_delete(self, uid: int) -> None:
        """取消关注用户"""

        self.log_adapter.info('user_follow_delete: 尝试取消关注用户 %s'
                              % uid)

        await self.post_json(
            'v1/user/follow/delete', data={'user_id': uid}
        )
