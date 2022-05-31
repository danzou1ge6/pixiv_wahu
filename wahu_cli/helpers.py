from datetime import datetime
from wahu_backend.aiopixivpy import IllustDetail
from wahu_backend.illust_bookmarking import IllustBookmark

from prettytable import PrettyTable, PLAIN_COLUMNS

IGNORE = True


def table_factory() -> PrettyTable:

    tbl = PrettyTable()
    tbl.set_style(PLAIN_COLUMNS)
    tbl.left_padding_width = tbl.right_padding_width = 1
    tbl.align = 'l'

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
    tbl.header = False
    _tbl_add_illust_detail(tbl, dtl)
    _tbl_add_bookmark_info(tbl, bm)

    return tbl.get_string()


def format_illust_detail(dtl: IllustDetail) -> str:

    tbl = table_factory()
    tbl.header = False
    _tbl_add_illust_detail(tbl, dtl)

    return tbl.get_string()
