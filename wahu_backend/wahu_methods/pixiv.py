import argparse
from typing import AsyncGenerator, Optional, Union

import click

from wahu_backend.aiopixivpy.datastructure_illust import PixivUserSummery

from ..aiopixivpy import (AccountSession, IllustDetail, PixivUserDetail,
                          PixivUserPreview, TrendingTagIllusts)
from ..aiopixivpy.ap_exceptions import AioPixivPyNotLoggedIn
from ..aiopixivpy.pixivpy_typing import (PixivRecomMode, PixivSearchTarget,
                                         PixivSort)
from ..wahu_core import WahuContext, wahu_methodize
from ..wahu_core.core_exceptions import WahuRuntimeError
from .lib_modded_argparser import ArgumentParser
from .lib_tag_utils import load_tag_model, process_illusts


def create_pixiv_query_parser() -> argparse.ArgumentParser:

    parser = ArgumentParser(prog='', exit_on_error=False)

    parser.add_argument('keyword', type=str, nargs='?')

    parser.add_argument('-n', '--new', action='store_true', help='新作')
    parser.add_argument('-r', '--recom', action='store_true', help='推荐插画')
    parser.add_argument('-f', '--follow', action='store_true', help='关注画师的最新插画')

    parser.add_argument('-i', '--iid', type=str, help='查询 IID. 用 `,` 分开多个 IID')
    parser.add_argument('-u', '--uid', type=int, help='查询用户 UID 的作品')
    parser.add_argument(
        '-b', '--bookmark', type=int, nargs='?', help='用户收藏的插画. 不提供 UID 则使用自己的', const=-1)

    parser.add_argument(
        '-R', '--rank', help='热门插画',
        choices=['day', 'week', 'month', 'day_male', 'day_female', 'week_original', 'week_rookie'])

    parser.add_argument(
        '-s', '--search',
        help='使用 Pixiv 提供的接口搜索插画. `ptag` for 部分标签, `etag` for 完整标签, `tc` for 标题和描述, `kw` for 关键词',
        choices=['ptag', 'etag', 'tc', 'kw']
    )
    parser.add_argument(
        '-S', '--sort',
        help='使用 Pixiv 搜索时的结果排序. `ddate` for 日期降序, `adate` for 日期升序, `dp` for 热门度降序',
        choices=['ddate', 'adate', 'dp'], default='ddate'
    )

    parser.add_argument(
        '-m', '--tag-model', action='store',
        help='使用标签逻辑回归模型计算插画得分'
    )
    parser.add_argument(
        '-F', '--filter', action='store', type=float, const=0.5, nargs='?',
        help='筛选得分'
    )

    return parser
pixiv_query_parser = create_pixiv_query_parser()


def create_puser_query_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='')

    parser.add_argument('keyword', type=str, nargs='?')
    parser.add_argument('-n', '--name', action='store_true', help='模糊搜索用户名')

    parser.add_argument('-u', '--uid', type=int, help='搜索用户 UID')

    parser.add_argument(
        '-f', '--follower', type=int, help='关注此用户的用户. 留空使用自己', nargs='?', const=-1)
    parser.add_argument(
        '-F', '--following', type=int, help='此用户关注的用户. 留空使用自己', nargs='?', const=-1)
    parser.add_argument(
        '-r', '--related', type=int, help='相关用户. 留空使用自己', nargs='?', const=-1)

    return parser
puser_query_parser = create_puser_query_parser()


class WahuPixivMethods:
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
    async def p_query(
        cls, ctx: WahuContext, qs: str
    ) -> AsyncGenerator[list[tuple[IllustDetail, float]], None]:

        args = click.parser.split_arg_string(qs)
        ns = pixiv_query_parser.parse_args(args)


        if ns.search is not None:
            target = {
                'ptag': 'partial_match_for_tags',
                'etag': 'exact_match_for_tags',
                'tc': 'title_and_caption',
                'kw': 'keyword'
            }[ns.search]

            sort = {
                'adate': 'date_asc',
                'ddate': 'date_desc',
                'dp': 'popular_desc'
            }[ns.sort]

            ret_gen = await cls.p_ilst_search(ctx, ns.keyword, target, sort)  # type: ignore

        elif ns.rank is not None:
            ret_gen = await cls.p_ilst_ranking(ctx, ns.rank)

        elif ns.recom:
            ret_gen = await cls.p_ilst_recom(ctx)
        elif ns.new:
            ret_gen = await cls.p_ilst_new(ctx)
        elif ns.follow:
            ret_gen = await cls.p_ilst_folow(ctx)

        elif ns.bookmark is not None:
            if ns.bookmark == -1:
                if ctx.papi.logged_in:
                    uid = ctx.papi.account_session.user_id  # type: ignore
                else:
                    raise AioPixivPyNotLoggedIn()
            else:
                uid = ns.bookmark
            ret_gen = await cls.p_user_bmilsts(ctx, uid)

        elif ns.iid is not None:
            iids = map(int, ns.iid.split(','))

            async def gen() -> AsyncGenerator[list[IllustDetail], None]:
                yield [
                    await ctx.papi.pool_illust_detail(iid) for iid in iids
                ]
            ret_gen = gen()

        elif ns.uid is not None:
            ret_gen = await cls.p_user_ilsts(ctx, ns.uid)

        else:
            ret_gen = await cls.p_ilst_search(ctx, ns.keyword, None, None)

        if ns.tag_model is None:
            async def unscored_ret_gen():
                async for illusts in ret_gen:
                    yield [(ilst, -1.) for ilst in illusts]
            return unscored_ret_gen()

        else:
            model = load_tag_model(ctx.config.tag_model_dir / (ns.tag_model + '.toml'))

            async def scored_ret_gen():
                async for illusts in ret_gen:

                    scores = process_illusts(model, illusts)
                    zipped = zip(illusts, scores)
                    if ns.filter is None:
                        yield list(zipped)
                    else:
                        yield [item for item in zipped if item[1] > ns.filter]

            return scored_ret_gen()


    @classmethod
    @wahu_methodize()
    async def p_query_user(
        cls, ctx: WahuContext, qs: str
    ) -> Union[AsyncGenerator[list[PixivUserPreview], None], int]:

        args = click.parser.split_arg_string(qs)
        ns = puser_query_parser.parse_args(args)


        if ctx.papi.logged_in:
            my_uid = ctx.papi.account_session.user_id  # type: ignore
        else:
            raise AioPixivPyNotLoggedIn()

        if ns.uid is not None:
            return ns.uid
        elif ns.follower is not None:
            follower = my_uid if ns.follower == -1 else ns.follower
            return await cls.p_user_follower(ctx, follower)
        elif ns.following is not None:
            following = my_uid if ns.following == -1 else ns.following
            return await cls.p_user_following(ctx, following)
        elif ns.related is not None:
            related = my_uid if ns.related == -1 else ns.related
            return await cls.p_user_related(ctx, related)

        else:  # elif ns.name
            return await cls.p_user_search(ctx, ns.keyword)


    @classmethod
    @wahu_methodize()
    async def p_query_help(cls, ctx: WahuContext) -> str:

        return pixiv_query_parser.format_help()

    @classmethod
    @wahu_methodize()
    async def p_query_user_help(cls, ctx: WahuContext) -> str:

        return puser_query_parser.format_help()

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
