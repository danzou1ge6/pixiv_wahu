import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Optional
import click

if TYPE_CHECKING:
    from wahu_backend.wahu_core import CliClickCtxObj

from wahu_backend.wahu_core.wahu_cli_util import wahu_cli_wrap
from wahu_backend.wahu_methods import WahuMethods

from helpers import report_dl_coro


NAME = '下载'
DESCRIPTION = '下载插画到临时下载目录或者任意指定的文件夹'


def mount(wexe: click.Group):

    @wexe.command()
    @click.argument('iid', type=int, required=True)
    @click.option(
        '--pages', '-p', type=int, multiple=True,
        help='指定下载页数，未指定则下载所有页'
    )
    @click.option(
        '--directory', '-d',
        type=click.Path(exists=False, file_okay=False, writable=True),
        help='指定下载目录，未指定则下载至配置的临时下载目录'
    )
    @click.option('--progress', '-g', is_flag=True, help='是否显示下载进度')
    @wahu_cli_wrap
    async def dl(
        cctx: click.Context,
        iid: int,
        pages: tuple[int],
        directory: Optional[str],
        progress: bool
    ):
        """下载插画
        """

        obj: CliClickCtxObj = cctx.obj
        pipe, wctx = obj.pipe, obj.wctx

        dtl = await wctx.papi.pool_illust_detail(iid)

        if len(pages) == 0:
            pages = tuple(range(dtl.page_count))

        if directory is None:
            dir_path = wctx.config.temp_download_dir
        else:
            dir_path = wctx.config.wpath(directory)

        fname_list = await WahuMethods.filename_for_illust(wctx, dtl, list(pages))
        path_list = [dir_path / f for f in fname_list]
        url_list = [dtl.image_origin[p] for p in pages]

        coro_list = [
            WahuMethods.download_image(wctx, url, pth)
            for url, pth in zip(url_list, path_list)
        ]

        if progress:
            tsk = asyncio.create_task(report_dl_coro(path_list, wctx, pipe))

        await asyncio.gather(*coro_list)

        if progress:
            tsk.cancel()  # type: ignore


