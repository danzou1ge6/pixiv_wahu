from json import JSONDecodeError
import json
from typing import Any
import aiohttp


class AioPixivPyError(Exception):
    pass

class AioPixivPyInvalidReturn(AioPixivPyError):
    """当 `Response.json()` 解析成功，但不符合预期时抛出"""
    def __init__(self, ret: dict[str, Any]):
        self.ret = ret

    def __str__(self) -> str:
        return '不合预期的返回：%s' % self.ret


class AioPixivPyInvalidHTTPStatus(AioPixivPyError):
    """当 `Response.ok == False` 时抛出"""
    def __init__(self, status: int, reason: Any, text: str):
        self.status = status
        self.reason = reason
        self.text = text

    def __str__(self) -> str:
        # 如果可以，展示解码 JSON 后的字典
        try:
            self.text = json.loads(self.text)
        except JSONDecodeError as _:
            pass

        finally:
            return '状态： %s ；原因： %s ；文本： %s'  \
                    % (self.status, self.reason, self.text)

class AioPixivPyNoRefreshToken(AioPixivPyError):
    """当无法登录时抛出"""

class AioPixivPyNotLoggedIn(AioPixivPyError):
    """`当试图调用需要登录的 Pixiv API 时抛出`"""
    def __init__(self):
        pass

    def __str__(self) -> str:
        return '没有 Access Token ，无法使用 Pixiv 服务'
