from asyncio import Event
from inspect import Traceback
from queue import Queue
from typing import Optional, AsyncGenerator, Generic, TypeVar

TP = TypeVar('TP')  # type payload

class CliIOPipe(AsyncGenerator[TP, TP], Generic[TP]):
    """使用异步生成器接口的命令行 IO 管道"""

    def __init__(self, max_size: int = -1):
        self.output_queue: Queue[TP] = Queue(maxsize=max_size)
        self.input_queue: Queue[TP] = Queue(maxsize=max_size)
        self.output_event = Event()
        self.input_event = Event()

        self.closed = False

    def put(self, val: TP):
        """输出"""

        self.output_queue.put(val)
        self.output_event.set()

    async def __anext__(self) -> TP:
        """
        前端读取一条输出，如果队列中没有则等待；
        如果管道关闭，抛出 `StopAsyncIteration`
        """

        if self.closed:
            raise StopAsyncIteration

        await self.output_event.wait()

        val = self.output_queue.get()

        if self.output_queue.empty():
            self.output_event.clear()

        return val

    async def asend(self, val: TP | None) -> TP:
        """前端输入，然后读取一条输出；如果输入 `None` ，则不进行输入"""

        if val is not None:
            self.input_queue.put(val)
            self.input_event.set()

        return await self.__anext__()

    async def get(self) -> TP:
        """等待前端输入"""

        await self.input_event.wait()

        val = self.input_queue.get()

        if self.input_queue.empty():
            self.input_event.clear()

        return val

    async def athrow(
        self,
        excpt_vale: Exception,
        excpt_type: Optional[type] = None,
        excpt_tcbk: Optional[Traceback] = None
    ):
        """在生成器中引起一条异常"""
        raise excpt_vale

    async def aclose(self):
        """设置管道关闭"""
        self.closed = True




