from pathlib import Path
import webbrowser

import click
from aiohttp import web

from .wahu_config import load_config
from .wahu_core import WahuContext
from .wahu_webapi.server import create_app

"""
PixivWahu 的命令行入口
"""



@click.group(invoke_without_command=True)
@click.pass_context
def pixiv_wahu_run(ctx):
    if ctx.invoked_subcommand is None:
        ctx.forward(run)


@pixiv_wahu_run.command()
@click.option('--port', '-p', type=int)
@click.option('--host', '-h', type=str)
@click.option('--config', '-c', type=click.Path(exists=True, dir_okay=False), default='./conf.toml')
@click.option('--browser/--no-browser', '-b/-n', is_flag=True, default=True)
def run(port, host, config, browser):

    config_obj = load_config(Path(config))


    if port is not None:
        config_obj.server_port = port
    if host is not None:
        config_obj.server_host = host

    ctx = WahuContext(config_obj)
    app = create_app(ctx)

    if browser:
        webbrowser.open(
            f'http://{ctx.config.server_host}:{ctx.config.server_port}/index.html')

    web.run_app(app, host=ctx.config.server_host, port=ctx.config.server_port)


if __name__ == '__main__':
    pixiv_wahu_run()
