from aiohttp import web

from wahu_backend.pixiv_image.image_getter import PixivImageGetError

from ..wahu_core import WahuContext
from .. import constants

def register(app: web.Application, ctx: WahuContext) -> None:
    """注册图片相关的 API"""

    routes = web.RouteTableDef()

    @routes.get(f'{constants.serverImageURL}''/{file_path:.+}')
    async def image(req: web.Request) -> web.Response:
        """从 Pixiv 服务器获取图片"""

        file_path = req.match_info['file_path']

        try:
            image = await ctx.image_pool.get_image(file_path)
        except PixivImageGetError as pige:
            app.logger.exception(pige, exc_info=True)
            return web.Response(
                status=503, reason='PixivImageGetError'
            )

        return web.Response(
            body=image, content_type='image/jpeg', headers={'Local': '0'}
        )


    @routes.get(f'{constants.repoImageURL}''/{repo_name:.+}/{fid:.+}')
    async def repoimage(req: web.Request) -> web.Response:
        """根据 FID 从本地获取文件"""

        repo_name = req.match_info['repo_name']
        fid = req.match_info['fid']

        if repo_name not in ctx.ilst_repos.keys():
            return web.Response(status=404, reason='找不到储存库')

        with await ctx.ilst_repos[repo_name](readonly=True) as ft:
            pth = ft.checkout(fid)

        if pth is not None:
            if not pth.exists():
                app.logger.warn('Server: repoimage: 索引中的文件 %s 不存在' % str(pth))
                return web.Response(status=404, reason="索引中的文件不存在")

            with open(pth, 'rb') as rf:
                return web.Response(body=rf.read(), content_type='image/jpeg')

        return web.Response(status=404, reason='找不到文件')

    @routes.get(f'{constants.illustDbImageURL}''/{db_name:.+}/{iid:\\d+}/{p:\\d+}')
    async def ilstdbimage(req: web.Request) -> web.Response:
        """根据数据库名和 IID 从本地或者服务器获取文件"""

        db_name = req.match_info['db_name']
        iid = int(req.match_info['iid'])
        p = int(req.match_info['p'])

        if db_name not in ctx.ilst_bmdbs.keys():
            return web.Response(status=404, reason='找不到插画收藏数据库')

        if db_name in ctx.ilst_bmdbs.keys():
            for ft_ctxman in ctx.repo_db_link.rfd(db_name):
                with await ft_ctxman(readonly=True) as ft:
                    pth = ft.checkout(f'{iid}-{p}')

                    if pth is not None:

                        if not pth.exists():
                            app.logger.warn('Server: ilstdbimage: 索引中的文件 %s 不存在' % str(pth))
                        else:
                            with open(pth, 'rb') as rf:
                                return web.Response(
                                    body=rf.read(),
                                    content_type='image/jpeg',
                                    headers={'Local': '1'}
                                )

        with await ctx.ilst_bmdbs[db_name](readonly=True) as ibd:
            ilst = ibd.query_detail(iid)

            if ilst is not None:
                if p >= ilst.page_count:
                    return web.Response(status=404, reason='找不到指定插画页')

                match ctx.config.fallback_image_size:
                    case 'original':
                        image_url = ilst.image_origin[p]
                    case 'medium':
                        image_url = ilst.image_medium[p]
                    case 'large':
                        image_url = ilst.image_large[p]
                    case 'square_medium':
                        image_url = ilst.image_sqmedium[p]
                    case _:
                        raise RuntimeError(f'不支持的图片大小 {ctx.config.fallback_image_size}')

                raise web.HTTPFound(f'/image/{image_url}')

            return web.Response(status=404, reason='数据库中找不到插画')

    app.add_routes(routes)
