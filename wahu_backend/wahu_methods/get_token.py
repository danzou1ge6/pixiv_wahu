import datetime
import hashlib
from base64 import urlsafe_b64encode
from hashlib import sha256
from secrets import token_urlsafe
from urllib.parse import urlencode
import aiohttp


from ..wahu_core import wahu_methodize, WahuContext
from .lib_logger import logger


REDIRECT_URI = "https://app-api.pixiv.net/web/v1/users/auth/pixiv/callback"
LOGIN_URL = "https://app-api.pixiv.net/web/v1/login"
CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"
HASH_SECRET = "28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c"


class TokenGetFail(Exception):
    """当获取 refresh_token 失败时抛出"""


class TokenGetter:
    host = "oauth.secure.pixiv.net"
    timeout = 10
    log_adapter = logger
    base_headers = {
        "app-os": "ios",
        "app-os-version": "14.6",
        "user-agent": "PixivIOSApp/7.13.3 (iOS 14.6; iPhone13,2)",
        'host': host
    }

    def __init__(self):
        self.code = ""
        self.code_verifier, self.code_challenge = self.oauth_pkce(self.s256)
        self.login_params = {
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
            "client": "pixiv-android",
        }


    def s256(self, data):
        """S256 transformation method."""

        return urlsafe_b64encode(sha256(data).digest()).rstrip(b"=").decode("ascii")

    def oauth_pkce(self, transform):
        """Proof Key for Code Exchange by OAuth Public Clients (RFC7636)."""

        code_verifier = token_urlsafe(32)
        code_challenge = transform(code_verifier.encode("ascii"))

        return code_verifier, code_challenge

    def get_login_url(self) -> str:
        login_url = f'{LOGIN_URL}?{urlencode(self.login_params)}'
        self.log_adapter.info(f'get_login_url: login_url={login_url}')
        return login_url

    async def login(self, code: str) -> str:
        """
        尝试通过 Code 获取 Refresh Token。
        :return: str: refresh token | None
        """

        self.log_adapter.info('login: attempting acquiring refresh_token')

        async with aiohttp.ClientSession(headers=self.base_headers) as session:

            async with session.post(
                "https://%s/auth/token" % self.host,
                data={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "code": code,
                    "code_verifier": self.code_verifier,
                    "grant_type": "authorization_code",
                    "include_policy": "true",
                    "redirect_uri": REDIRECT_URI,
                },
                ssl=False,
                timeout=10,
                headers=self.get_header()
            ) as resp:
                rst = await resp.json()

        if "refresh_token" in rst:
            return rst["refresh_token"]
        else:
            raise TokenGetFail("Request Error.\nResponse: " + str(rst))


    @classmethod
    def get_header(cls):

        headers = {}
        local_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        headers["x-client-time"] = local_time
        headers["x-client-hash"] = hashlib.md5(
            (local_time + HASH_SECRET).encode("utf-8")
        ).hexdigest()
        return headers
token_getter = TokenGetter()


class WahuGetTokenMethods:

    @classmethod
    @wahu_methodize()
    async def token_get_loginurl(
        cls, ctx: WahuContext
    ) -> str:
        """获得登录页面 url"""

        return token_getter.get_login_url()

    @classmethod
    @wahu_methodize()
    async def token_submit_code(
        cls, ctx: WahuContext, code: str
    ) -> str:
        """提交 code ，并获取 refresh_token"""

        rt = await token_getter.login(code)

        if ctx.config.refresh_token_path is None:
            logger.warn('token_submit_code: 未设定 refresh_token_path ， refresh_token 不会被保存')
        else:
            with open(ctx.config.refresh_token_path, 'w', encoding='utf-8') as wf:
                wf.write(rt)

        return rt
