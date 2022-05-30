from datetime import datetime
from wahu_backend.aiopixivpy import IllustDetail
from wahu_backend.illust_bookmarking import IllustBookmark

from prettytable import PrettyTable, PLAIN_COLUMNS

IGNORE = True

def format_bookmarked_illust_detail(dtl: IllustDetail, bm: IllustBookmark) -> str:

    tbl = PrettyTable()
    tbl.set_style(PLAIN_COLUMNS)
    tbl.header = False
    tbl.left_padding_width = tbl.right_padding_width = 1
    tbl.align = 'l'
    tbl.add_rows([
        ('标题', dtl.title),
        ('描述', dtl.caption),
        ('IID', dtl.iid),
        ('画师', f'{dtl.user.name} - {dtl.user.uid}'),
        ('页数', dtl.page_count),
        ('添加于', datetime.fromtimestamp(bm.add_timestamp)),
        ('收藏页码数', bm.pages),
        ('收藏数', dtl.total_bookmarks),
        ('看过', dtl.total_view)
    ])

    return tbl.get_string()
