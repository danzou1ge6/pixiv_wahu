from inspect import Traceback
from typing import Generic, Optional, TypeVar
from asyncio import Lock

from .abc import DependingDatabase


T = TypeVar('T', bound=DependingDatabase)


class CtxInstance(Generic[T]):

    __slots__ = ('dd', 'lock', 'readonly')

    def __init__(self, dd: T, lock: Lock, readonly: bool=False):
        self.dd = dd
        self.lock = lock
        self.readonly = readonly

    def __enter__(self) -> T:

        self.dd.connect()
        return self.dd

    def __exit__(self,
                 excpt_type: Optional[type] = None,
                 excpt_vale: Optional[Exception] = None,
                 excpt_tcbk: Optional[Traceback] = None):
        """异常照常抛出"""

        self.dd.close(commit=(not self.readonly))
        self.lock.release()

class DatabaseContextManager(Generic[T]):
    """对 DependingDatabase 类对象进行上下文管理"""

    __slots__ = ('dd', 'lock')

    def __init__(self, dd: T):
        self.dd = dd
        self.lock = Lock()

    async def __call__(self, readonly: bool=False) -> CtxInstance[T]:

        await self.lock.acquire()
        return CtxInstance(self.dd, self.lock, readonly)
