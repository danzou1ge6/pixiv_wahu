import asyncio
import os
from pathlib import Path
from typing import Any, Literal
import webbrowser

import click
from aiohttp import web

from .wahu_config import load_config
from .wahu_core import WahuContext, CliClickCtxObj, CliIOPipeTerm
from .wahu_webapi.server import create_app

"""
PixivWahu 的命令行入口
"""


port_deco = click.option(
    '--port', '-p', type=int, help='指定端口，覆盖配置文件'
)
host_deco = click.option(
    '--host', '-h', type=str, help='指定主机名，覆盖配置文件'
)
conf_deco = click.option(
    '--config', '-c', type=click.Path(exists=True, dir_okay=False),
    default=lambda: os.environ.get('PIXIVWAHU_CONFPATH', 'conf.toml'),
    help='指定配置文件，覆盖环境变量 PIXIVWAHU_CONFPATH ，默认值 conf.toml'
)
browser_deco = click.option(
    '--browser/--no-browser', '-b/', is_flag=True, default=True,
    help='是否自动打开浏览器，默认是'
)
logging_deco = click.option(
    '--log-level', '-l',
    type=click.Choice(['ERROR', 'WARNING', 'INFO', 'DEBUG'], case_sensitive=False),
    help='设定根记录器的日记级别，覆盖配置文件'
)
silent_deco = click.option(
    '--quiet', '-q', is_flag=True,
    help='将根记录器的日志级别设置为 WARNING'
)


@click.group(invoke_without_command=True)
@port_deco
@host_deco
@conf_deco
@browser_deco
@logging_deco
@silent_deco
@click.pass_context
def pixiv_wahu_run(
    cctx: click.Context,
    port: int,
    host: str,
    config: str,
    browser: bool,
    log_level: Literal['ERROR', 'WARNING', 'INFO', 'DEBUG'],
    quiet: bool
):
    """运行 PixivWahu

    缺省子命令将调用子命令 ui
    """

    config_obj = load_config(Path(config))

    if port is not None:
        config_obj.server_port = port
    if host is not None:
        config_obj.server_host = host

    if quiet:
        log_level = 'WARNING'

    if log_level is not None:
        config_obj.pylogging_cfg_dict['root']['level'] = log_level

    wctx = WahuContext(config_obj)

    cctx.obj = wctx

    if cctx.invoked_subcommand is None:
        cctx.forward(ui)


def print_exe_help(cctx: click.Context, param: click.Parameter, value: Any):
    if value:
        click.echo(cctx.obj.wexe.get_help(cctx))
        cctx.exit()

@pixiv_wahu_run.command(
    context_settings=dict(ignore_unknown_options=True)
)
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.option(
    '--help', is_flag=True, is_eager=True, expose_value=False, callback=print_exe_help)
@click.pass_context
def exe(cctx, args: list[str]):
    """执行 WahuCli 命令
    """

    wctx: WahuContext = cctx.obj
    pipe = CliIOPipeTerm()

    async def main():
        wctx.wexe.main(
            args,
            prog_name='',
            obj=CliClickCtxObj(wctx, pipe),
            standalone_mode=False
        )
        await pipe.close_event.wait()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

@pixiv_wahu_run.command()
@browser_deco
@click.pass_context
def ui(cctx, browser):
    """启动 WebUI
    """

    wctx: WahuContext = cctx
    app = create_app(wctx)

    if browser:
        webbrowser.open(
            f'http://{wctx.config.server_host}:{wctx.config.server_port}/index.html')

    web.run_app(app, host=wctx.config.server_host, port=wctx.config.server_port)


if __name__ == '__main__':
    pixiv_wahu_run()
