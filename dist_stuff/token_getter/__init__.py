# -*- coding:utf-8 -*-
#!/bin/python
import datetime
import hashlib
from base64 import urlsafe_b64encode
from hashlib import sha256
import json
from pathlib import Path
from secrets import token_urlsafe
from urllib.parse import urlencode
import webbrowser

import aiohttp
from aiohttp import web
from wahu_backend.manual_dns import ManualDNSClient
import logging

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

LICENSE = """
MIT License

Copyright (c) 2020 Trii Hsia

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


REDIRECT_URI = "https://app-api.pixiv.net/web/v1/users/auth/pixiv/callback"
LOGIN_URL = "https://app-api.pixiv.net/web/v1/login"
CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"
HASH_SECRET = "28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c"

class TokenGetter(ManualDNSClient):
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
        super().__init__()


    def s256(self, data):
        """S256 transformation method."""

        return urlsafe_b64encode(sha256(data).digest()).rstrip(b"=").decode("ascii")

    def oauth_pkce(self, transform):
        """Proof Key for Code Exchange by OAuth Public Clients (RFC7636)."""

        code_verifier = token_urlsafe(32)
        code_challenge = transform(code_verifier.encode("ascii"))

        return code_verifier, code_challenge

    def get_login_url(self):
        login_url = f'{LOGIN_URL}?{urlencode(self.login_params)}'
        self.log_adapter.info(f'get_login_url: login_url={login_url}')
        return login_url

    async def login(self, code):
        """
        尝试通过 Code 获取 Refresh Token。
        :return: str: refresh token | None
        """
        await self._check_env()

        self.log_adapter.info('login: attempting acquiring refresh_token')

        async with self.session.post(
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
            self.log_adapter.error("Request Error.\nResponse: " + str(rst))


    @classmethod
    def get_header(cls):

        headers = {}
        local_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        headers["x-client-time"] = local_time
        headers["x-client-hash"] = hashlib.md5(
            (local_time + HASH_SECRET).encode("utf-8")
        ).hexdigest()
        return headers


def create_app():
    app = web.Application()
    tg = TokenGetter()

    routes = web.RouteTableDef()

    @routes.get('/')
    async def mainpage(req: web.Request):
        login_url = tg.get_login_url()

        html_path = Path(__file__).parent / 'main.html'
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
            html = html.replace('[% login_url %]', login_url)
            return web.Response(text=html, content_type='text/html')

    @routes.get('/submitcode')
    async def submit_code(req: web.Request):
        code = req.query.get('code')

        if code is None:
            app.logger.error('未提供 code')
            return web.Response(status=503)

        app.logger.info('收到code='+code)
        rt = await tg.login(code)

        if rt is None:
            app.logger.error('获取 refresh token 失败')
            return web.Response(status=503)

        app.logger.info('refresh_token='+rt)
        app.logger.info('写入./user/refresh_token.txt')
        with open('./user/refresh_token.txt', 'wb') as wf:
            wf.write(rt.encode('utf-8'))

        return web.Response(text=json.dumps({'refresh_token': rt}))

    @routes.get('/pixivbiulicense')
    async def pixivbiu_license(req: web.Request):
        return web.Response(text=LICENSE)

    app.add_routes(routes)

    return app

def run_app(app):
    print('将在http://127.0.0.1:28687上运行服务器')
    webbrowser.open('http://127.0.0.1:28687')
    web.run_app(app, port=28687, host="127.0.0.1")

def main():
    app = create_app()
    run_app(app)

if __name__ == "__main__":
    main()
    