import asyncio
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Union
import os

from wahu_backend.aiopixivpy import IllustDetail
from wahu_backend.illust_bookmarking import IllustBookmark

from prettytable import PrettyTable, PLAIN_COLUMNS

if TYPE_CHECKING:
    from wahu_backend.wahu_core import WahuContext, CliIOPipeTerm
    from wahu_backend.wahu_core.wahu_cli import CliIoPipeABC

IGNORE = True

"""
WahuCli 的高级助手函数
"""


def table_factory() -> PrettyTable:

    tbl = PrettyTable()
    tbl.set_style(PLAIN_COLUMNS)
    tbl.left_padding_width = tbl.right_padding_width = 1
    tbl.align = 'l'
    tbl.header = False

    return tbl

def _tbl_add_illust_detail(tbl: PrettyTable, dtl: IllustDetail) -> None:

    tbl.add_rows([
        ('标题', dtl.title),
        ('描述', dtl.caption),
        ('IID', dtl.iid),
        ('画师', f'{dtl.user.name} - {dtl.user.uid}'),
        ('页数', dtl.page_count),
        ('收藏数', dtl.total_bookmarks),
        ('看过', dtl.total_view)
    ])

def _tbl_add_bookmark_info(tbl: PrettyTable, bm: IllustBookmark) -> None:

    tbl.add_rows([
        ('添加于', datetime.fromtimestamp(bm.add_timestamp)),
        ('收藏页码数', bm.pages),
    ])

def format_bookmarked_illust_detail(dtl: IllustDetail, bm: IllustBookmark) -> str:

    tbl = table_factory()
    _tbl_add_illust_detail(tbl, dtl)
    _tbl_add_bookmark_info(tbl, bm)

    return tbl.get_string()


def format_illust_detail(dtl: IllustDetail) -> str:

    tbl = table_factory()
    _tbl_add_illust_detail(tbl, dtl)

    return tbl.get_string()

async def report_dl_coro(
    path_list: list[Path],
    wctx: 'WahuContext',
    pipe: 'CliIoPipeABC',
    interval: float=0.3
):
    """将下载进度输出到 pipe"""

    path_str_list = [str(p) for p in path_list]

    pipe.putline('')

    while True:
        progs = list(filter(
            lambda x: x.descript in path_str_list,
            wctx.image_pool.dl_stats
        ))

        if len(progs) !=0:
            break

        await asyncio.sleep(0.1)

    while True:
        progs = list(filter(
            lambda x: x.descript in path_str_list,
            wctx.image_pool.dl_stats
        ))

        if len(progs) == 0:
            break

        tbl = table_factory()
        tbl.field_names = ['状态', '文件名', '已下载/共', '%']
        tbl.header = True
        tbl.add_rows([
            (p.status,
             os.path.split(p.descript)[-1] if p.descript is not None else 'Unknown',
             f'{p.downloaded_kb} / {p.total_kb}',
             f'{p.downloaded_size * 100 / p.total_size:.0f}%' if p.total_size is not None else '/')
            for p in progs
        ])

        text = tbl.get_string()

        pipe.put(text=text, rewrite=True)

        await asyncio.sleep(interval)
