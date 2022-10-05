import logging
from typing import Any, MutableMapping


class AioPixivpyLoggerAdapter(logging.LoggerAdapter):
    """在 PixivAPI 的日志前打印 user_name"""
    
    def __init__(self, logger: logging.Logger):
        self.user_name = '未登录'
        self.logger = logger

    def set_user_name(self, user_name: str) -> None:
        self.user_name = user_name

    def process(
        self,
        msg: Any,
        kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        return 'PixivAPI[%s] %s' % (self.user_name, msg), kwargs
