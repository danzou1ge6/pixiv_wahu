import logging
from asyncio import Semaphore
from typing import Any, MutableMapping, Optional

import aiohttp

from ..http_typing import HTTPHeaders
from ..manual_dns import ManualDNSClient
from .download_status import DownloadProgressTracker
from .logger import logger

HOSTS = [
    '210.140.92.140:443', '210.140.92.137:443', '210.140.92.139:443',
    '210.140.92.142:443', '210.140.92.134:443', '210.140.92.141:443',
    '210.140.92.143:443', '210.140.92.135:443', '210.140.92.136:443'
]

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0'


class PixivImageGetError(ConnectionError):

    def __init__(self, image_address: str, host: Optional[str]):
        self.image_address = image_address
        self.host = host


class PixivImageGetterLogAdapter(logging.LoggerAdapter):
    """在 FileTracer 的日志前打印 FileTracer.name"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def process(
        self, msg: Any,
        kwargs: MutableMapping[str,
                               Any]) -> tuple[Any, MutableMapping[str, Any]]:
        return 'PixivImageGetter: %s' % msg, kwargs


class PixivImageGetter(ManualDNSClient):

    host_name = 'i.pximg.net'

    def __init__(
        self,
        host: Optional[str] = None,
        timeout: float = 5,
        chunk: int = 2048,
        connection_limit: int = 7,
        num_parallel: int = 3,
        record_size: int = 100
    ) -> None:
        """
        - `:param timeout:` 全局的超时
        - `:param host:` IP 地址；如果提供了，就不会再通过 DNS 查询
        """
        self.timeout: float = timeout

        self.base_headers: HTTPHeaders = {
            'Host': self.host_name,
            'User-Agent': USER_AGENT,
            'Accept-Encoding': '',
            'Referer': 'https://www.pixiv.net'
        }

        if host is not None:
            self.host = host

        self.session: aiohttp.ClientSession

        self.dl_stats: DownloadProgressTracker = DownloadProgressTracker(
            record_size=record_size)
        self.chunk_size: int = chunk
        self.connection_limit = connection_limit

        self.log_adapter = PixivImageGetterLogAdapter(logger)

        self.sem = Semaphore(num_parallel)

        super().__init__()

    async def get_image(self, file_path: str, descript: Optional[str]=None) -> bytes:
        """
        从 i.pximg.net 获取图片
        - `:param file_path` 形如 `img-original/img/2011/07/23/00/01/42/20514048_p0.jpg`
        """

        await self._check_env()

        url = f'https://{self.host}/{file_path}'

        with self.dl_stats.new(
            url,
            descript=url.split('/')[-1] if descript is None else descript
        ) as st:

            async with self.sem:

                logger.info('PixivImageGetter: get_image: 尝试获取 %s' % file_path)

                try:
                    async with self.session.get(url, ssl=True) as resp:

                        total_size = resp.headers.get('Content-Length', None)
                        if total_size is None:
                            total_size = resp.headers.get('content-length')
                        st.start(total_size)

                        image = bytes()

                        async for chk in resp.content.iter_chunked(self.chunk_size):
                            image += chk
                            st.update(self.chunk_size)

                        return image

                except aiohttp.ClientError as client_error:
                    raise PixivImageGetError(file_path, self.host) from client_error
