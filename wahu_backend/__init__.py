import asyncio
import functools
import os
from pathlib import Path
from typing import Any, Coroutine, Literal
import webbrowser

import click
from aiohttp import web

from .wahu_config import load_config, WahuConfig, conf_side_effects
from .wahu_core import WahuContext
from .wahu_webapi.server import create_app
from .wahu_client.cli_client import main as cli_client_main


"""
PixivWahu 的命令行入口
"""

def _run_in_new_loop(coro: Coroutine[Any, Any, Any]) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)


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
    '--browser/--no-browser', '-b/-n', is_flag=True, default=True,
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
@browser_deco
@conf_deco
@port_deco
@host_deco
@logging_deco
@silent_deco
@click.pass_context
def _run(
    cctx: click.Context,
    browser: bool,
    config: str,
    port: int,
    host: str,
    log_level: Literal['ERROR', 'WARNING', 'INFO', 'DEBUG'],
    quiet: bool,
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

    cctx.obj = config_obj

    if cctx.invoked_subcommand is None:
        cctx.invoke(ui, browser=browser)

@_run.command(
    context_settings=dict(ignore_unknown_options=True)
)
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.option(
    '--help', is_flag=True)
@click.pass_context
def exe(cctx: click.Context, args: tuple[str], help: bool):
    """执行 WahuCli 命令
    """

    args_list = list(args)

    if help:
        args_list.append('--help')

    async def main():
        ret_code = await cli_client_main(args_list, cctx.obj)
        if ret_code != 0:
            print(f'退出代码: {ret_code}')

    _run_in_new_loop(main())

@_run.command()
@browser_deco
@click.pass_context
def ui(
    cctx: click.Context,
    browser: bool,
):
    """启动 WebUI
    """

    config_obj: WahuConfig = cctx.obj
    conf_side_effects(config_obj)

    with WahuContext(config_obj) as wctx:

        app = create_app(wctx)

        if browser:
            host = '127.0.0.1' if wctx.config.server_host == '0.0.0.0' else wctx.config.server_host
            webbrowser.open(
                f'http://{host}:{wctx.config.server_port}/index.html'
            )

        web.run_app(app, host=wctx.config.server_host, port=wctx.config.server_port)


run = functools.partial(_run.main, standalone_mode=False)  # 确保 atexit hook 被触发

if __name__ == '__main__':
    run()
