import asyncio
import dataclasses
from ..wahu_core import wahu_methodize, WahuContext


class WahuMiscMethods:

  @wahu_methodize()
  @staticmethod
  async def wahu_download(
    ctx: WahuContext, iids: list[int]
  ) -> None:
    """下载 `iids` 到本地"""

    async with ctx.papi.ready:
      dtls = [await ctx.papi.pool_illust_detail(iid) for iid in iids]

    coro_list = []
    for dtl in dtls:

      async def coro():
        for url in dtl.image_origin:
          ext = url.split('.')[-1]
          fname = ctx.config.file_name_template.format(
            **dataclasses.asdict(dtl)) + f'.{ext}'

          image = await ctx.image_pool.get_image(
            url,
            fname
          )

          with open(ctx.config.temp_download_dir / fname, 'wb') as wf:
            wf.write(image)

      coro_list.append(coro())

    [asyncio.create_task(coro) for coro in coro_list]

