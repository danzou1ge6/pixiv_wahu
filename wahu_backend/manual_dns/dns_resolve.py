import asyncio
import traceback
import aiohttp
import logging

from .logger import logger

# DNS_URLS = [
#     'https://doh.dns.sb/dns-query',
#     'https://dns.alidns.com/resolve',
#     'https://cloudflare-dns.com/dns-query',
#     'https://doh.pub/dns-query'
# ]  # 这些都寄了

DNS_URLS = ['https://45.11.45.11/dns-query']  # 目前来看最稳定的
USE_SSL = True

def set_doh_url(urls: list[str]) -> None:
    """全局修改 DNS over HTTPS 的 URL"""

    global DNS_URLS
    DNS_URLS = urls

def set_doh_ssl(ssl: bool) -> None:
    """全局修改 DNS over HTTPS 是否使用 SSL"""
    global USE_SSL
    USE_SSL = ssl

    if not ssl:
        logger.warn('set_doh_ssl: 进行 DNS 解析时将不验证 SSL 证书')


class DNSResolveError(Exception):
    def __init__(self):
        self.host_name = None
        self.dns_url = None
        raise NotImplementedError

class DNSResolveQueryError(DNSResolveError):
    def __init__(self, host_name: str, dns_url: str):
        self.host_name = host_name
        self.dns_url = dns_url

    def __str__(self) -> str:
        return f'使用 DNS URL {self.dns_url} 解析 {self.host_name} 时出现 aiohttp.ClientError'


class DNSResolveReadError(DNSResolveError):
    def __init__(self, host_name: str, dns_url: str, dns_ret: dict):
        self.host_name = host_name
        self.dns_url = dns_url
        self.dns_ret = dns_ret

    def __str__(self) -> str:
        return f'使用 DNS URL {self.dns_url} 解析 {self.host_name} ' \
               f'时收到不合预期的返回 {self.dns_ret}'

class DNSResolveAllFailError(DNSResolveError):
    def __init__(self, host_name: str, dns_urls: list[str]):
        self.host_name = host_name
        self.dns_urls = dns_urls


async def _resolve_host_using(client: aiohttp.ClientSession,
                              host_name: str,
                              dns_url: str,
                              timeout: float=5) -> list[str]:
    try:
        async with client.get(dns_url, ssl=USE_SSL,
                              params={'name': host_name, 'type': 'A', 'do': 'false', 'cd': 'false'},
                              timeout=timeout) as resp:
            json_data = await resp.json()

            try:
                host_list = [ans['data'] for ans in json_data['Answer']]

            except KeyError as _:
                raise DNSResolveReadError(host_name, dns_url, json_data)

            logger.debug('_resolve_host_using: 使用 %s 解析 %s 得到 %s'
                         % (dns_url, host_name, host_list))
            return host_list

    except aiohttp.ClientError as client_error:
        raise DNSResolveQueryError(host_name, dns_url) \
            from client_error



async def resolve_host(host_name: str, timeout: float=5) -> list[str]:
    """
    使用 `DNS_URLS` 中的 DNS 服务器解析主机名
    """

    async with aiohttp.ClientSession() as client:

        # 将所有解析任务加入调度
        task_list = [
            asyncio.create_task(
                _resolve_host_using(client,
                                    host_name,
                                    dns_url,
                                    timeout=timeout)) for dns_url in DNS_URLS
        ]

        # 协程使用各个 `dns_url` 解析主机名
        result = []
        for task in task_list:
            try:
                result.extend(await task)
            except DNSResolveError as dre:
                logger.warning(str(dre) + ':\n' + traceback.format_exc())

    if result == []:
        raise DNSResolveAllFailError(host_name, DNS_URLS)

    logger.debug('resolve_dns: 解析 %s 得到 %s' % (host_name, result))

    result = list(filter(lambda x: x[0] in ('1', '2'), result))

    return result


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    async def main():
        hosts = await resolve_host('i.pixiv.net')
        print(hosts)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
