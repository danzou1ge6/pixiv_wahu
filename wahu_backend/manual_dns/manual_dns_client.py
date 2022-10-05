import logging
from random import choice
from typing import Optional, Union
from asyncio import Lock

import aiohttp

from ..http_typing import HTTPHeaders
from .dns_resolve import resolve_host, DNSResolveError


class ManualDNSClientError(DNSResolveError):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class ManualDNSClient:
    """
    手动进行 DNS 解析的 HTTP 客户端，包裹 `aiohttp.ClientSession`
        （为什么要这么做呢？你懂我意思吧 [doge] ）
    不可实例化\n
    继承后需要添加：
    - `:member host_name:` 进行 DNS 解析的主机名\n
    在 `__init__` 方法中需要创建：
    - `:attr timeout:` 全局超时 **必须在 `__init__` 中设定**
    - `:attr base_headers:` 设置给 `session` 的请求头 **必须在 `__init__` 中设定**
    - `:attr log_adapter:` 日志适配器，用于添加上下文信息 **必须在 `__init__` 中设定**
    - `:attr host:` 解析得到的 ip
    - `:attr session:` `aiohttp.ClientSession` 实例
    """

    __slots__ = ['host_name', 'timeout', 'connection_limit', 'host', 'session', 'env_chk_lock']

    host_name: str

    def __init__(self, connection_limit: int = 100):
        self.timeout: float = 5
        self.connection_limit: int = connection_limit

        self.host: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_headers: Union[HTTPHeaders, None]
        self.log_adapter: Union[logging.LoggerAdapter, logging.Logger]

        self.env_chk_lock = Lock()

    async def create_session(self) -> None:
        conn = aiohttp.TCPConnector(limit=self.connection_limit)
        self.session = aiohttp.ClientSession(headers=self.base_headers,
                                             connector=conn)
        self.log_adapter.debug('create_session: 创建 aiohttp.ClientSession')

    async def close_session(self) -> None:
        if self.session is not None:
            await self.session.close()
        self.log_adapter.debug('close_session: 关闭 aiohttp.ClientSession')

    async def resolve_host(self) -> None:

        host_list = await resolve_host(self.host_name,
                                              timeout=self.timeout)

        if self.session is None:
            await self.create_session()
            assert self.session is not None

        for host in host_list:
            try:
                async with self.session.get(f'https://{host}', verify_ssl=False) as resp:
                    self.host = host
                    self.log_adapter.info('resolve_host: 使用主机 %s' % self.host)
                    return

            except aiohttp.ClientError as ce:
                self.log_adapter.warn('resolve_host: 主机 %s 无法访问' % host)

        raise ManualDNSClientError('解析得到的所有主机均不可用')


    async def _check_env(self):
        """确保完成了 DNS 解析，以及是否创建了 `ClientSession`"""
        async with self.env_chk_lock:

            if self.session is None:
                await self.create_session()

            if self.host is None:
                await self.resolve_host()


