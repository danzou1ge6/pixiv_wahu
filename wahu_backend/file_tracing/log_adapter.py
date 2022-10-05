import logging
from typing import Any, MutableMapping


class FileTracerLoggingAdapter(logging.LoggerAdapter):
    """在 `FileTracer` 的日志前打印 `FileTracer.name`"""

    def __init__(self, name: str, logger: logging.Logger):
        self.ft_name = name
        self.logger = logger

    def process(
        self, msg: Any,
        kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        return 'FileTracr[%s] %s' % (self.ft_name, msg), kwargs
