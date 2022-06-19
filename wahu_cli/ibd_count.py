import itertools
from typing import TYPE_CHECKING, Iterable, Literal, Optional

import click
from collections import Counter
from wahu_backend.aiopixivpy.datastructure_illust import PixivUserSummery


if TYPE_CHECKING:
    from wahu_backend.aiopixivpy.datastructure_illust import IllustTag
    from wahu_backend.wahu_core import CliClickCtxObj

from wahu_backend.wahu_core.wahu_cli_util import less, wahu_cli_wrap

from helpers import table_factory


IGNORE = True  # 不被自动加载

def mount(parent_group: click.Group):

    @parent_group.command()
    @click.argument('name', type=str, required=True)
    @click.argument(
        'target', type=click.Choice(['tag', 'user']), default='tag'
    )
    @click.option(
        '--num', '-n', type=int, default=10,
        help='显示的结果数. -1 代表无限制'
    )
    @wahu_cli_wrap
    async def count(
        cctx: click.Context,
        name: str,
        target: Literal['tag', 'user'],
        num: Optional[int]
    ):
        """对数据库 NAME 中的 TARGET 进行计数

        仅能统计数据库中已经保存了详情的插画
        """

        obj: 'CliClickCtxObj' = cctx.obj
        wctx, pipe = obj.wctx, obj.pipe

        if name not in wctx.ilst_bmdbs.keys():
            raise KeyError(f'fatal: 数据库 {name} 不存在')

        tbl = table_factory()

        if num == -1:
            num = None

        with await wctx.ilst_bmdbs[name](readonly=True) as ibd:

            if target == 'tag':
                tags: Iterable[IllustTag] = itertools.chain(
                    *(r[0] for r in ibd.illusts_te.select_cols(cols=['tags']))
                )

                cntr = Counter(tags)

                result = cntr.most_common(num)

                tbl.field_names = ['名', '译', '次数']
                tbl.add_rows([
                    (it.name, it.translated if it.translated is not None else '', n)
                    for it, n in result
                ])

            else:
                users: Iterable[PixivUserSummery] = (
                    r[0] for r in ibd.illusts_te.select_cols(cols=['user'])
                )

                cntr = Counter(users)

                result = cntr.most_common(num)

                tbl.field_names = ['UID', '名', '次数']
                tbl.add_rows([(u.uid, u.name, n) for u, n in result])

        await less(tbl.get_string(), pipe)
