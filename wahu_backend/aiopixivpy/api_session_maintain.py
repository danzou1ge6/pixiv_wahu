import asyncio
import dataclasses
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Optional

import toml

from .ap_exceptions import AioPixivPyNoRefreshToken
from .api_base import AccountSession
from .api_main import PixivAPI


class MaintainedSessionPixivAPI(PixivAPI):
    """
    通过保存本地文件尽量复用 `access_token` \n
    P.S.此处出现的 「session / 会话」 一词与 `aiohttp.ClientSession` 无关
    """

    def __init__(
        self,
        session_path: Path,
        refresh_token_path: Optional[Path],
        timeout: float = 5.0,
        host: Optional[str] = None,
        language: str = 'en-us',
        ilst_pool_size: int = 1000,
        connection_limit: int = 20,
    ):
        """
        - `:param session_path:` 保存会话信息的路径
        - `:param refresh_token_path:` 保存 `refresh_token` 的路径
        """

        self.session_path: Path = session_path
        self.refresh_token_path: Optional[Path] = refresh_token_path

        self.login_lock = asyncio.Lock()  # 用于确保 `get_logged_api`` 时不重复登录

        super().__init__(
            timeout=timeout, host=host, language=language,
            ilst_pool_size=ilst_pool_size, connection_limit=connection_limit)

        if self.refresh_token_path is None:
            self.log_adapter.warn('refresh_token_path 未设定，将无法获取 access_token')

        self.attemp_load_account_session()

    def _write_account_session(self, a_s: AccountSession) -> None:
        """将会话信息写入文件"""
        d = dataclasses.asdict(a_s)
        ts = toml.dumps({'account_session': d})

        ts = '# 这份文件保存了账户会话的信息，可在 `expire_at` 前用于 Pixiv API\n\n' + ts

        with open(self.session_path, 'w', encoding='utf-8') as wf:
            wf.write(ts)

    def _read_account_session(self) -> Optional[AccountSession]:
        """从文件中读取会话信息"""
        try:
            d = toml.load(self.session_path)

        except toml.TomlDecodeError:
            self.log_adapter.warning('读取 account_session : 解析 toml 失败')
            return None

        try:
            d = d['account_session']
            return AccountSession(
                d['user_name'],
                d['user_id'],
                d['expire_at'],
                d['access_token'],
            )

        except KeyError:
            self.log_adapter.warning('读取 account_session : 解析 toml 成功，但内容损坏')
            return None

    def _validate_account_session(self, account_session: AccountSession) -> bool:
        """校验从文件中读取的会话信息是否过期；用户 ID 是否相符"""

        if datetime.now() > account_session.expire_at:
            self.log_adapter.debug(
                '校验 account_session : 已于 %s 过期'
                % account_session.expire_at
            )
            return False

        if self.account_session is not None and \
                account_session.user_id != self.account_session.user_id:

            self.log_adapter.debug(
                '校验 account_session : 用户 ID 不符 : account_session.user_id=%d '
                'papi.user_id=%d'
                % (account_session.user_id, self.account_session.user_id)
            )
            return False

        return True

    def _load_account_session(self) -> Optional[AccountSession]:
        """从文件读取会话信息并校验；失败则返回 `None`"""

        if not self.session_path.exists():
            self.log_adapter.debug('读取 account_session : 文件不存在')
            return None

        account_session = self._read_account_session()

        if account_session is None:
            return None

        if not self._validate_account_session(account_session):
            return None

        return account_session

    def _read_refresh_token(self) -> str:
        """从文件读取 refresh_token"""

        if self.refresh_token_path is None:
            raise AioPixivPyNoRefreshToken('未设定 refresh_token_path')

        if not self.refresh_token_path.exists():
            raise AioPixivPyNoRefreshToken(
                '未找到 %s ，无法读取 refresh_token'
                % str(self.refresh_token_path))

        with open(self.refresh_token_path, 'r', encoding='utf-8') as rf:
            return rf.read().lstrip().rstrip()

    def attemp_load_account_session(self) -> bool:

        account_session = self._load_account_session()

        # 如果成功从文件读取了会话信息
        if account_session is not None:
            self.account_session = account_session

            self.log_adapter.set_user_name(account_session.user_name)

            self.log_adapter.info(
                '从文件读取了 access_token ，将在 %s 过期'
                % account_session.expire_at
            )

            return True
        return False

    async def ensure_loggedin(self) -> None:
        """获取一个确保已经登录的 `PixivAPI`"""

        async with self.login_lock:

            # 如果已登录且未过期
            if self.account_session is not None:
                if self.account_session.expire_at > datetime.now():
                    return
                self.log_adapter.info('access_token 已过期')
            else:
                self.log_adapter.info('未登录')

            if self.attemp_load_account_session():
                return

            # 使用 refresh_token 重新认证
            self.log_adapter.info('尝试重新认证 refresh_token')

            await self.auth_refresh_token(self._read_refresh_token())

            assert self.account_session is not None

            self.log_adapter.info(
                '重新认证成功，将在 %s 过期'
                % self.account_session.expire_at
            )

            self._write_account_session(self.account_session)

            return

    @property
    @asynccontextmanager
    async def ready(self) -> AsyncGenerator['MaintainedSessionPixivAPI', None]:
        """
        使用 `async with MaintainedSessionPixivAPI.ready:` 来保证登录 \n
        这个方法是为了使 `ensure_loggedin` 用起来更为优雅
        """

        await self.ensure_loggedin()
        yield self
