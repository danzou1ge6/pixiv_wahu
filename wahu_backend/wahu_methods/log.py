import logging
from asyncio import Event
from queue import Queue
import traceback
from typing import AsyncGenerator, Generic, TypeVar

from ..wahu_core import WahuContext, wahu_methodize
from .lib_logger import logger

T = TypeVar('T')
class QueueBuffer(Generic[T]):
    """用队列来缓存数据"""

    def __init__(self, maxsize: int):
        self.queue = Queue[T](maxsize)
        self.available_event = Event()

    def write(self, data: T):
        self.queue.put(data)
        self.available_event.set()

    async def get(self) -> T:
        await self.available_event.wait()
        data = self.queue.get()

        if self.queue.empty():
            self.available_event.clear()

        return data


class BufferHandler(logging.Handler):
    def __init__(self, buffer: QueueBuffer[logging.LogRecord], level: int):
        super().__init__()

        self.buffer = buffer
        self.level = level

    def emit(self, rec: logging.LogRecord) -> None:
        self.buffer.write(rec)


class WahuLoggingMethods:

    @classmethod
    @wahu_methodize()
    async def wahu_logger_client(
        cls, ctx: WahuContext
    ) -> AsyncGenerator[tuple[int, str], None]:
        """返回一个生成器，每次调用生成器获得一条日志"""

        logger.info('开始报告日志')

        buffer = QueueBuffer[logging.LogRecord](9999)
        hdlr = BufferHandler(buffer, logging.WARNING)

        root_logger = logging.getLogger()
        root_logger.addHandler(hdlr)

        async def gen():

            try:
                while True:
                    rec = await buffer.get()
                    yield rec.levelno, rec.getMessage()

            except StopAsyncIteration:
                root_logger.removeHandler(hdlr)

        return gen()

