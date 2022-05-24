import asyncio
import logging
import sys
from aiohttp import web

from .image_getter import PixivImageGetter


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

def create_app() -> web.Application:
    app = web.Application()

    image_getter = PixivImageGetter()

    async def get_image(req: web.Request) -> web.Response:
        file_path = req.match_info['file_path']

        image = await image_getter.get_image(file_path)

        resp = web.Response(body=image, content_type='image/jpeg')
        return resp

    async def on_app_shutdown(app: web.Application) -> None:
        await image_getter.close_session()


    app.add_routes([web.get('/{file_path:.+}', get_image)])
    app.on_shutdown.append(on_app_shutdown)

    return app

if __name__ == '__main__':
    app = create_app()

    import click

    @click.command()
    @click.option('--port', '-p', type=int, default=1402)
    @click.option('--host', '-h', type=str, default='127.0.0.1')
    def main(port: int, host: str) -> None:
        web.run_app(app, host=host, port=port)

    main()
