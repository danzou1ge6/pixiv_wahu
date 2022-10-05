from collections import OrderedDict
import dataclasses
import functools
import hashlib
from datetime import datetime, timedelta
from typing import (Any, Callable, Concatenate, Literal, Optional, ParamSpec,
                    TypeVar)

import aiohttp

from ..manual_dns.manual_dns_client import ManualDNSClient
from .ap_exceptions import (AioPixivPyInvalidHTTPStatus,
                            AioPixivPyInvalidReturn, AioPixivPyNotLoggedIn)
from .datastructure_illust import IllustDetail
from .log_adapter import AioPixivpyLoggerAdapter
from .logger import logger
from .pixivpy_typing import HTTPData, HTTPHeaders, URLParams


@dataclasses.dataclass(slots=True)
class AccountSession:
    user_name: str
    user_id: int
    expire_at: datetime
    access_token: str


T = TypeVar('T')
P = ParamSpec('P')


class BasePixivAPI(ManualDNSClient):
    """
    PixivAPI 客户端的基类
    - `:member client_id, client_secret, hash_secret:` 魔法，不太懂，有大佬教教？
    - `:member host_name:` API 服务器名，仅用于 IP 地址的解析
    - `:member auth_host_name:` 登录 API 服务器名，仅用于登录
    - `:member api_host_name:` API 服务器名，用于使用 Pixiv 功能
    - `:member _filter_param:` pixivpy 中出现的 `filter` URL 参数，
                               似乎设置成 `for_ios` 就好
    """

    client_id = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
    client_secret = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"
    hash_secret = "28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c"

    host_name = 'public-api.secure.pixiv.net'
    auth_host_name = 'oauth.secure.pixiv.net'
    api_host_name = 'app-api.pixiv.net'

    _filter_param = 'for_ios'

    def __init__(
        self, timeout: float = 5.0, host: Optional[str] = None,
        language: str = 'en-us', ilst_pool_size: int = 1000,
        connection_limit: int = 20):
        """
        - `:param timeout:` 全局的超时
        - `:param host:` IP 地址；如果提供了，就不会再通过 DNS 查询
        """

        self.log_adapter: AioPixivpyLoggerAdapter = AioPixivpyLoggerAdapter(
            logger)
        self.timeout = timeout

        self.base_headers: HTTPHeaders = {
            'Host':  self.api_host_name,
            'User-Agent': 'PixivIOSApp/7.13.3 (iOS 14.6; iPhone13,2)',
            'App-OS': 'ios',
            'App-OS-Version': '14.6',
            'Accept-Language': language,
            'Accept-Encoding': '',
            'Referer': 'https://www.pixiv.net'
        }

        self.host: str
        self.session: aiohttp.ClientSession


        if host is not None:
            self.host = host

        self.log_adapter.debug('init: 超时设置为 %s' % timeout)

        # 保存账户登录信息
        self.account_session: Optional[AccountSession] = None

        self.ilst_pool: OrderedDict[int, IllustDetail] = OrderedDict()
        self.ilst_pool_size = ilst_pool_size

        self.connection_limit = connection_limit

        super().__init__()

    async def _session_json_call(
        self,
        method_name: Literal['POST', 'GET'],
        url: str,
        params: Optional[URLParams] = None,
        data: Optional[HTTPData] = None,
        headers: Optional[HTTPHeaders] = None,
        **kwds: Any
    ) -> HTTPData:
        """
        调用 `self.session` \n
        如果存在 `self.account_session.access_token` ，则 headers 中将添加
        - `:param method:` 应为 `ClientSession.get | post | ...`
        - `:return:` 解析 JSON 后的字典
        """
        if self.account_session is not None:
            if headers is None:
                headers = {}
            headers |= {'Authorization':
                        f'Bearer {self.account_session.access_token}'}

        if method_name == 'GET':
            method = self.session.get
        elif method_name == 'POST':
            method = self.session.post

        # 可能抛出 aiohttp.ClientError
        async with method(
                f'https://{self.host}/{url}',
                ssl=False,
                params=params,
                data=data,
                headers=headers,
                **kwds
        ) as resp:
            if resp.ok:
                j = await resp.json()
            else:
                rt = await resp.text()
                raise AioPixivPyInvalidHTTPStatus(
                    resp.status, resp.reason, rt)


        return j

    async def get_json(
        self,
        url: str,
        params: Optional[URLParams] = None,
        headers: Optional[HTTPHeaders] = None,
        **kwds: Any
    ) -> HTTPData:
        """GET 方法发起请求"""

        await self._check_env()

        return await self._session_json_call(
            'GET',
            url,
            params=params,
            headers=headers,
            **kwds
        )

    async def post_json(
        self,
        url: str,
        params: Optional[URLParams] = None,
        data: Optional[HTTPData] = None,
        headers: Optional[HTTPHeaders] = None,
        **kwds: Any
    ) -> HTTPData:
        """POST 方法发起请求"""

        await self._check_env()

        return await self._session_json_call(
            'POST',
            url,
            params=params,
            data=data,
            headers=headers,
            **kwds
        )

    async def auth_refresh_token(self, refresh_token: str) -> HTTPData:
        """
        使用 `refresh_token` 登录
        :return: pixiv 返回的数据（处理后，移除了冗余和敏感信息（指 `refresh_token`））
        """

        headers = self.base_headers.copy()

        local_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        headers['X-Client-Time'] = local_time
        headers['X-Client-Hash'] = hashlib.md5(
            (local_time + self.hash_secret).encode('utf-8')).hexdigest()
        headers['Host'] = self.auth_host_name  # 会覆写 base_headers['Host']

        data = {
            "get_secure_url": 1,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        data['grant_type'] = 'refresh_token'
        data['refresh_token'] = refresh_token

        self.log_adapter.info('auth_refresh_token: 尝试登陆')

        ret = await self.post_json('auth/token', headers=headers, data=data)

        try:
            self.account_session = AccountSession(
                ret['user']['name'],  # type: ignore
                int(ret['user']['id']),  # type: ignore
                datetime.now() + timedelta(seconds=int(ret['expires_in'])),  # type: ignore
                ret['access_token']  # type: ignore
            )

            self.log_adapter.set_user_name(self.account_session.user_name)

        except KeyError as ke:
            raise AioPixivPyInvalidReturn(ret) from ke

        self.log_adapter.info('auth_refresh_token: 登陆成功 user_id=%s' %
                              self.account_session.user_id)

        ret.pop('refresh_token')
        ret.pop('response')  # 删除冗余信息

        return ret

    @classmethod
    def strip_api_host_name(cls, url: str) -> str:
        return url.replace(f'https://{cls.api_host_name}/', '')

    @property
    def logged_in(self):
        """是否登录. 同时检查 `access_token` 是否过期"""

        if self.account_session is not None:
            if self.account_session.expire_at < datetime.now():
                self.account_session = None
        return self.account_session is not None



def check_login(
    f: Callable[Concatenate[Any, P], T]
) -> Callable[Concatenate[Any, P], T]:
    """检查是否登录，否则抛出异常"""
    @functools.wraps(f)
    def r(self: Any, *args: P.args, **kwds: P.kwargs) -> T:
        if not self.logged_in:
            raise AioPixivPyNotLoggedIn()
        return f(self, *args, **kwds)
    return r
