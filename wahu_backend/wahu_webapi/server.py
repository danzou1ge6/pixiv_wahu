from pathlib import Path
from aiohttp import web

from ..wahu_core import WahuContext
from .api_image import register as reg_image_api
from .api_rpc import register as reg_rpc_api
from .api_logger import register as reg_logger_api
from .api_report_dl import register as reg_report_dl_api

"""
后端服务器的工厂函数
"""


def create_app(ctx: WahuContext) -> web.Application:

    app = web.Application()

    reg_image_api(app, ctx)
    reg_rpc_api(app, ctx)

    reg_logger_api(app)
    reg_report_dl_api(app, ctx)

    if not Path('static').exists():
        app.logger.warn('create_app: 资源文件夹 static 不存在')
    else:
        app.add_routes([
            web.static('/', 'static')
        ])

    async def ctx_cleanup(app: web.Application):
        await ctx.cleanup()

    app.on_shutdown.append(ctx_cleanup)

    return app

