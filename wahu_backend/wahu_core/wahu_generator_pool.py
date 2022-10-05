from typing import Any, AsyncGenerator, Iterable, Optional
from random import sample
from collections import OrderedDict

from .core_exceptions import WahuAsyncGeneratorPoolKeyError

def _generate_gid(not_in: Iterable) -> str:

    while True:
        n = ''.join(sample('abcdefghijklmnopqrstuvwxyz0123456789', 8))

        if n not in not_in:
            break

    return n

class WahuAsyncGeneratorPool:
    """维护一个异步生成器池"""

    def __init__(self, size: int):
        self.size = size
        self.pool: OrderedDict[str, AsyncGenerator[Any, None]] = OrderedDict()

    def new(self, g: AsyncGenerator[Any, None]) -> str:
        """将一个新的异步生成器添加到池中，如果超出 `size` ，先进先出地抛弃旧生成器"""

        if len(self.pool) >= self.size:
            self.pool.popitem(last=False)

        k = _generate_gid(self.pool.keys())
        self.pool[k] = g
        return k

    def pop(self, key: str) -> bool:
        """删除异步生成器. 存在则返回 True ，否则返回 False"""

        if key in self.pool.keys():
            self.pool.pop(key)
            return True
        return False

    async def call(self, key: str, send_val: Any = None) -> Optional[Any]:
        """
        根据 `new` 方法返回的标识符 `key` 调用池中的异步生成器 \n
        如果池中没有，抛出 `WahuAsyncGeneratorPoolKeyError` \n
        如果迭代结束，返回 `None`
        """

        g = self.pool.get(key, None)

        if g is None:
            raise WahuAsyncGeneratorPoolKeyError(key)

        try:
            r = await g.asend(send_val)
            return r

        except StopAsyncIteration:

            self.pool.pop(key)
            return None
