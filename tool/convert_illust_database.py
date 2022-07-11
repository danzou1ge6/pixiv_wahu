from wahu_backend.illust_bookmarking import IllustBookmarkDatabase
from wahu_backend.aiopixivpy.datastructure_processing import process_pixiv_illust_dict
from wahu_backend.aiopixivpy.datastructure_illust import IllustDetail
import asyncio
from pathlib import Path
import sqlite3
import click
import json

import sys
sys.path.append('./')

"""将 pixman2 数据库转换为 PixivWahu 数据库"""


def load_illusts(input: Path) -> list[IllustDetail]:
    db_con = sqlite3.connect(input)
    ret = db_con.execute('SELECT detail FROM illusts').fetchall()
    db_con.close()
    return [process_pixiv_illust_dict(json.loads(r[0])) for r in ret]


async def write_bookmark_db(ibd: IllustBookmarkDatabase, illusts: list[IllustDetail]) -> None:
    ibd.connect()
    [await ibd.set_bookmark(ilst.iid, list(range(ilst.page_count))) for ilst in illusts]
    ibd.illusts_te.insert(illusts)
    ibd.close()


@click.command()
@click.option('--input', '-i', type=click.Path(exists=True, dir_okay=False))
@click.option('--output', '-o', type=click.Path(dir_okay=False))
def cvt(input: str, output: str) -> None:
    input_p = Path(input)
    output_p = Path(output)
    illusts = load_illusts(input_p)
    ibd = IllustBookmarkDatabase(output_p.stem, output_p)
    asyncio.run(write_bookmark_db(ibd, illusts))


if __name__ == '__main__':
    cvt()
