from typing import AsyncGenerator, Optional, TypeVar

from ..aiopixivpy import AccountSession, IllustDetail, PixivUserDetail
from ..aiopixivpy.datastructure_user import PixivUserPreview
from ..aiopixivpy.pixivpy_typing import (PixivRecomMode, PixivSearchTarget,
                                         PixivSort)
from ..wahu_core import WahuContext, wahu_methodize
from ..wahu_core.core_exceptions import WahuRuntimeError

RT = TypeVar('RT')

class WahuPixivMethods:
    """
    与 PixivAPI 相关的方法
    """

    @wahu_methodize()
    @staticmethod
    async def p_account_session(ctx: WahuContext) -> Optional[AccountSession]:
        """如果登陆了，返回会话信息，否则返回 None"""

        if ctx.papi.logged_in:
            return ctx.papi.account_session
        else:
            return None

    @wahu_methodize()
    @staticmethod
    async def p_attempt_login(ctx: WahuContext) -> AccountSession:
        """尝试登陆"""

        await ctx.papi.ensure_loggedin()

        if ctx.papi.account_session is None:
            raise WahuRuntimeError('p_attempt_login: account_session is None')

        return ctx.papi.account_session

    @wahu_methodize(middlewares=[])
    @staticmethod
    async def p_user_ilsts(
        ctx: WahuContext, uid: int
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """`PixivAPI.user_illusts`"""

        async with ctx.papi.ready:
            return ctx.papi.user_illusts(uid)

    @wahu_methodize(middlewares=[])
    @staticmethod
    async def p_user_bmilsts(
        ctx: WahuContext, uid: int
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """`PixivAPI.user_bookmark_illusts`"""

        async with ctx.papi.ready:
            return ctx.papi.user_bookmarks_illusts(uid)

    @wahu_methodize(middlewares=[])
    @staticmethod
    async def p_user_detail(
        ctx: WahuContext, uid: int
    ) -> PixivUserDetail:
        """`PixivAPI.user_detail`"""

        async with ctx.papi.ready:
            return await ctx.papi.user_detail(uid)

    @wahu_methodize(middlewares=[])
    @staticmethod
    async def p_ilst_detail(
        ctx: WahuContext, iid: int
    ) -> IllustDetail:
        """`PixivAPI.pool_illust_detail`"""

        async with ctx.papi.ready:
            return await ctx.papi.pool_illust_detail(iid)

    @wahu_methodize()
    @staticmethod
    async def p_ilst_recom(ctx: WahuContext
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """`PixivAPI.illust_recommended"""

        async with ctx.papi.ready:
            return ctx.papi.illust_recommended()

    @wahu_methodize()
    @staticmethod
    async def p_ilst_related(
        ctx: WahuContext, iid: int
    ) -> AsyncGenerator[list[IllustDetail], None]:
        """`PixivAPI.illust_related`"""

        async with ctx.papi.ready:
            return ctx.papi.illust_related(iid)

    @wahu_methodize()
    @staticmethod
    async def p_ilst_ranking(
        ctx: WahuContext, mode: PixivRecomMode
    ) -> AsyncGenerator[list[IllustDetail], None]:

        async with ctx.papi.ready:
            return ctx.papi.illust_ranking(mode)

    @wahu_methodize()
    @staticmethod
    async def p_ilst_folow(ctx: WahuContext
    ) -> AsyncGenerator[list[IllustDetail], None]:

        async with ctx.papi.ready:
            return ctx.papi.illust_follow()

    @wahu_methodize()
    @staticmethod
    async def p_ilst_new(ctx: WahuContext
    ) -> AsyncGenerator[list[IllustDetail], None]:

        async with ctx.papi.ready:
            return ctx.papi.illust_new()

    @wahu_methodize()
    @staticmethod
    async def p_ilst_search(
        ctx: WahuContext, keyword: str,
        target: Optional[PixivSearchTarget], sort: Optional[PixivSort]
    ) -> AsyncGenerator[list[IllustDetail], None]:

        if target is None:
            target = 'partial_match_for_tags'
        if sort is None:
            sort = 'date_desc'

        async with ctx.papi.ready:
            return ctx.papi.search_illust(
                keyword,
                search_target=target,
                sort=sort
            )

    @wahu_methodize()
    @staticmethod
    async def p_ilstbm_add(
        ctx: WahuContext, iids: list[int]
    ) -> None:

        async with ctx.papi.ready:
            [await ctx.papi.illust_bookmark_add(iid) for iid in iids]

    @wahu_methodize()
    @staticmethod
    async def p_ilstbm_rm(
        ctx: WahuContext, iids: list[int]
    ) -> None:

        async with ctx.papi.ready:
            [await ctx.papi.illust_bookmark_delete(iid) for iid in iids]

    @wahu_methodize()
    @staticmethod
    async def p_user_search(
        ctx: WahuContext, keyword: str
    ) -> AsyncGenerator[list[PixivUserPreview], None]:

        async with ctx.papi.ready:
            return ctx.papi.search_user(keyword)

    @wahu_methodize()
    @staticmethod
    async def p_user_follower(
        ctx: WahuContext, uid: int
    ) -> AsyncGenerator[list[PixivUserPreview], None]:

        async with ctx.papi.ready:
            return ctx.papi.user_follower(uid)

    @wahu_methodize()
    @staticmethod
    async def p_user_following(
        ctx: WahuContext, uid: int
    ) -> AsyncGenerator[list[PixivUserPreview], None]:

        async with ctx.papi.ready:
            return ctx.papi.user_following(uid)

    @wahu_methodize()
    @staticmethod
    async def p_user_related(
        ctx: WahuContext, uid: int
    ) -> AsyncGenerator[list[PixivUserPreview], None]:

        async with ctx.papi.ready:
            return ctx.papi.user_related(uid)

    @wahu_methodize()
    @staticmethod
    async def p_user_follow_add(
        ctx: WahuContext, uid: int
    ) -> None:

        async with ctx.papi.ready:
            await ctx.papi.user_follow_add(uid)

    @wahu_methodize()
    @staticmethod
    async def p_user_follow_rm(
        ctx: WahuContext, uid: int
    ) -> None:

        async with ctx.papi.ready:
            await ctx.papi.user_follow_delete(uid)
