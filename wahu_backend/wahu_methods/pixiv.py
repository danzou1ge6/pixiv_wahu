from typing import AsyncGenerator, Optional, TypeVar

from ..aiopixivpy import (AccountSession, IllustDetail, PixivUserDetail,
                          PixivUserPreview, TrendingTagIllusts)
from ..aiopixivpy.pixivpy_typing import (PixivRecomMode, PixivSearchTarget,
                                         PixivSort)
from ..wahu_core import WahuContext, WahuMethodsCollection, wahu_methodize
from ..wahu_core.core_exceptions import WahuRuntimeError

RT = TypeVar('RT')

class WahuPixivMethods(WahuMethodsCollection):
    """
    与 PixivAPI 相关的方法
    """

    @classmethod
    @wahu_methodize()
    async def p_account_session(cls, ctx: WahuContext) -> Optional[AccountSession]:
        """如果登陆了，返回会话信息，否则返回 None"""

        if ctx.papi.logged_in:
            return ctx.papi.account_session
        else:
            return None

    @classmethod
    @wahu_methodize()
    async def p_attempt_login(cls, ctx: WahuContext) -> AccountSession:
        """尝试登陆"""

        await ctx.papi.ensure_loggedin()

        if ctx.papi.account_session is None:
            raise WahuRuntimeError('p_attempt_login: account_session is None')

        return ctx.papi.account_session

    @classmethod
    @wahu_methodize()
    async def p_user_ilsts(
        cls, ctx: WahuContext, uid: int
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """`PixivAPI.user_illusts`"""

        return ctx.papi.user_illusts(uid)

    @classmethod
    @wahu_methodize()
    async def p_user_bmilsts(
        cls, ctx: WahuContext, uid: int
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """`PixivAPI.user_bookmark_illusts`"""

        return ctx.papi.user_bookmarks_illusts(uid)

    @classmethod
    @wahu_methodize()
    async def p_user_detail(
        cls, ctx: WahuContext, uid: int
    ) -> PixivUserDetail:
        """`PixivAPI.user_detail`"""

        return await ctx.papi.user_detail(uid)

    @classmethod
    @wahu_methodize()
    async def p_ilst_detail(
        cls, ctx: WahuContext, iid: int
    ) -> IllustDetail:
        """`PixivAPI.pool_illust_detail`"""

        return await ctx.papi.pool_illust_detail(iid)

    @classmethod
    @wahu_methodize()
    async def p_ilst_recom(cls, ctx: WahuContext
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """`PixivAPI.illust_recommended"""

        return ctx.papi.illust_recommended()

    @classmethod
    @wahu_methodize()
    async def p_ilst_related(
        cls, ctx: WahuContext, iid: int
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """`PixivAPI.illust_related`"""

        return ctx.papi.illust_related(iid)

    @classmethod
    @wahu_methodize()
    async def p_ilst_ranking(
        cls, ctx: WahuContext, mode: PixivRecomMode
    ) -> AsyncGenerator[list[IllustDetail], None]:

        return ctx.papi.illust_ranking(mode)

    @classmethod
    @wahu_methodize()
    async def p_ilst_folow(cls, ctx: WahuContext
    ) -> AsyncGenerator[list[IllustDetail], None]:

        return ctx.papi.illust_follow()

    @classmethod
    @wahu_methodize()
    async def p_ilst_new(cls, ctx: WahuContext
    ) -> AsyncGenerator[list[IllustDetail], None]:

        return ctx.papi.illust_new()

    @classmethod
    @wahu_methodize()
    async def p_ilst_search(
        cls, ctx: WahuContext, keyword: str,
        target: Optional[PixivSearchTarget], sort: Optional[PixivSort]
    ) -> AsyncGenerator[list[IllustDetail], None]:

        if target is None:
            target = 'partial_match_for_tags'
        if sort is None:
            sort = 'date_desc'

        return ctx.papi.search_illust(
            keyword,
            search_target=target,
            sort=sort
        )

    @classmethod
    @wahu_methodize()
    async def p_ilstbm_add(
        cls, ctx: WahuContext, iids: list[int]
    ) -> None:

        [await ctx.papi.illust_bookmark_add(iid) for iid in iids]

    @classmethod
    @wahu_methodize()
    async def p_ilstbm_rm(
        cls, ctx: WahuContext, iids: list[int]
    ) -> None:

        [await ctx.papi.illust_bookmark_delete(iid) for iid in iids]

    @classmethod
    @wahu_methodize()
    async def p_user_search(
        cls, ctx: WahuContext, keyword: str
    ) -> AsyncGenerator[list[PixivUserPreview], None]:

        return ctx.papi.search_user(keyword)

    @classmethod
    @wahu_methodize()
    async def p_user_follower(
        cls, ctx: WahuContext, uid: int
    ) -> AsyncGenerator[list[PixivUserPreview], None]:

        return ctx.papi.user_follower(uid)

    @classmethod
    @wahu_methodize()
    async def p_user_following(
        cls, ctx: WahuContext, uid: int
    ) -> AsyncGenerator[list[PixivUserPreview], None]:

        return ctx.papi.user_following(uid)

    @classmethod
    @wahu_methodize()
    async def p_user_related(
        cls, ctx: WahuContext, uid: int
    ) -> AsyncGenerator[list[PixivUserPreview], None]:

        return ctx.papi.user_related(uid)

    @classmethod
    @wahu_methodize()
    async def p_user_follow_add(
        cls, ctx: WahuContext, uid: int
    ) -> None:

        await ctx.papi.user_follow_add(uid)

    @classmethod
    @wahu_methodize()
    async def p_user_follow_rm(
        cls, ctx: WahuContext, uid: int
    ) -> None:

        await ctx.papi.user_follow_delete(uid)

    @classmethod
    @wahu_methodize()
    async def p_trending_tags(
        cls, ctx: WahuContext
    ) -> list[TrendingTagIllusts]:

        return await ctx.papi.trending_tags_illust()
