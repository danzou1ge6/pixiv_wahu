from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from wahu_backend.wahu_core import CliClickCtxObj

from wahu_backend.wahu_core.wahu_cli_util import wahu_cli_wrap

from helpers import table_factory

NAME = '登录'
DESCRIPTION = '登录 Pixiv'


def mount(wexe: click.Group):

    @wexe.command()
    @click.option('--silent', '-s', is_flag=True, help='不打印会话信息')
    @wahu_cli_wrap
    async def login(cctx: click.Context, silent: bool):
        """尝试登陆，并打印会话信息
        """

        obj: CliClickCtxObj = cctx.obj

        if not obj.wctx.papi.logged_in:
            obj.pipe.putline('未登录. 尝试登陆')

        await obj.wctx.papi.ensure_loggedin()

        ac = obj.wctx.papi.account_session
        if ac is None:
            raise RuntimeError('登陆失败')

        if not silent:
            tbl = table_factory()
            tbl.add_rows([
                ('UID', ac.user_id),
                ('用户名', ac.user_name),
                ('AccessToken', ac.access_token),
                ('过期于', ac.expire_at)
            ])

            obj.pipe.putline(tbl.get_string())
