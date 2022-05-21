from asyncio import StreamWriter
import asyncio
from functools import partial
import logging
import dataclasses
from aiohttp import web

from ..wahu_core import WahuContext

async def start_reporting_dl(ctx: WahuContext, app: web.Application):

    async def report_dl_status():
        while True:
            if 'ws' in app.keys():
                ws: web.WebSocketResponse = app['ws']
                if not ws.closed:

                    status = list(ctx.image_pool.dl_stats)

                    if status != []:
                        await ws.send_json({
                            'type': 'dl_progress',
                            'return': [dataclasses.asdict(s)
                                        for s in status]
                        })

            await asyncio.sleep(0.5)

    dl_status_report_task = asyncio.create_task(report_dl_status())

    yield

    dl_status_report_task.cancel()

def register(app: web.Application, ctx: WahuContext):
    app.cleanup_ctx.append(partial(start_reporting_dl, ctx))
