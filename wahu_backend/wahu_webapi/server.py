from pathlib import Path
from aiohttp import web
from importlib import resources

from ..wahu_core import WahuContext
from .api_image import register as reg_image_api
from .api_rpc import register as reg_rpc_api
from .api_logger import register as reg_logger_api
from .api_report_dl import register as reg_report_dl_api

"""
后端服务器的工厂函数
"""

reousece_search_paths = [
    Path('./'),
    Path(__file__).parent.parent,
    Path(__file__).parent.parent.parent
]


def create_app(ctx: WahuContext) -> web.Application:

    app = web.Application()

    reg_image_api(app, ctx)
    reg_rpc_api(app, ctx)

    reg_logger_api(app)
    reg_report_dl_api(app, ctx)

    try:
        res_path = resources.path('wahu_frontend', 'index.html').__enter__()
        app.logger.debug('使用 wahu_frontend 包中的静态文件')
        app.add_routes([web.static('/', res_path.parent)])
    except ModuleNotFoundError:
        if Path('static').exists():
            app.logger.debug('使用工作目录下的 static 文件夹')
            app.add_routes([web.static('/', 'static')])
        else:
            app.logger.warn('create_app: 资源文件夹 static 不存在，假设作为调试服务器运行')

    async def ctx_cleanup(app: web.Application):
        await ctx.cleanup()

    app.on_shutdown.append(ctx_cleanup)

    return app

