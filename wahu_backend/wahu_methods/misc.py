import asyncio
import itertools
from pathlib import Path
from typing import Optional

from wahu_backend.aiopixivpy.datastructure_illust import IllustDetail

from ..wahu_core import wahu_methodize, WahuContext
from ..wahu_core.core_exceptions import WahuRuntimeError

from .logger import logger

class WahuMiscMethods:

    @classmethod
    @wahu_methodize()
    async def filename_for_illust(
        cls, ctx: WahuContext, dtl: IllustDetail, pages: list[int]=[]
    ) -> list[str]:
        """获得插画 `dtl` 的下载文件名"""

        if len(pages) == 0:
            pages = list(range(dtl.page_count))

        return [
            ctx.config.file_name_template.format(dtl, p) + \
                f'.{dtl.image_origin[p].split(".")[-1]}'
            for p in pages
        ]

    @classmethod
    @wahu_methodize()
    async def download_image(
        cls, ctx: WahuContext, url: str, path: Path
    ) -> None:
        """下载 `url` 到 `Path`"""

        if path.exists():
            logger.warn(f'文件 {path} 已存在')

        image = await ctx.image_pool.get_image(url, descript=str(path))

        with open(path, 'wb') as wf:
            wf.write(image)

    @classmethod
    @wahu_methodize()
    async def wahu_download(
        cls, ctx: WahuContext, iids: list[int]
    ) -> None:
        """下载 `iids` 到本地"""

        dtls = [await ctx.papi.pool_illust_detail(iid) for iid in iids]

        path_gen = itertools.chain(
            *(
                (ctx.config.temp_download_dir / fname
                 for fname in await cls.filename_for_illust(ctx, dtl))
                for dtl in dtls
            )
        )

        url_gen = itertools.chain(*(dtl.image_origin for dtl in dtls))

        coro_gen = (
            cls.download_image(ctx, url, pth)
            for url, pth in zip(url_gen, path_gen)
        )

        [asyncio.create_task(coro) for coro in coro_gen]

    @classmethod
    @wahu_methodize(middlewares=[])
    async def get_config(
        cls, ctx: WahuContext, name: str
    ) -> str:

        if not hasattr(ctx.config, name):
            raise WahuRuntimeError(f'没有配置项 {name}')

        return str(getattr(ctx.config, name))

