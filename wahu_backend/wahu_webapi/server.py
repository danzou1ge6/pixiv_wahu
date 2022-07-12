from pathlib import Path
from aiohttp import web
from importlib import resources

from ..wahu_core import WahuContext
from .api_image import register as reg_image_api
from .api_rpc import register as reg_rpc_api

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

    try:
        res_path = resources.path('wahu_frontend', 'index.html').__enter__()
        app.logger.debug('Server: 使用 wahu_frontend 包中的静态文件')
        app.add_routes([web.static('/', res_path.parent)])
    except ModuleNotFoundError:
        if Path('dist/wahu_frontend').exists():
            app.logger.debug('Server: 使用 dist/wahu_frontend 文件夹')
            app.add_routes([web.static('/', 'dist/wahu_frontend')])
        else:
            app.logger.warn('Server: 缺少前端文件')

    return app

