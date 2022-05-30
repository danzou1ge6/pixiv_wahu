import asyncio

from ..wahu_core import wahu_methodize, WahuContext
from ..wahu_core.core_exceptions import WahuRuntimeError

class WahuMiscMethods:

    @classmethod
    @wahu_methodize()
    async def wahu_download(
        cls, ctx: WahuContext, iids: list[int]
    ) -> None:
        """下载 `iids` 到本地"""

        dtls = [await ctx.papi.pool_illust_detail(iid) for iid in iids]

        coro_list = []
        for dtl in dtls:

            async def coro():
                for i, url in enumerate(dtl.image_origin):
                    ext = url.split('.')[-1]
                    fname = ctx.config.file_name_template.format(
                        dtl, i) + f'.{ext}'

                    image = await ctx.image_pool.get_image(
                        url,
                        fname
                    )

                    with open(ctx.config.temp_download_dir / fname, 'wb') as wf:
                        wf.write(image)

            coro_list.append(coro())

        [asyncio.create_task(coro) for coro in coro_list]

    @classmethod
    @wahu_methodize(middlewares=[])
    async def get_config(
        cls, ctx: WahuContext, name: str
    ) -> str:

        if not hasattr(ctx.config, name):
            raise WahuRuntimeError(f'没有配置项 {name}')

        return str(getattr(ctx.config, name))

