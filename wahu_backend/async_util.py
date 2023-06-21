from typing import TypeVar, AsyncIterable, Optional

T = TypeVar('T')
async def alist(g: AsyncIterable[T], count: Optional[int] = None) -> list[T]:
    """
    将一个 `AsyncIterable` 中元素提取到一个 `list` 中
    - `:param count:` 提取的最大元素数量
    """

    ret = []

    if count is None:
        try:
            async for item in g:
                ret.append(item)
        except StopAsyncIteration:
            return ret
        finally:
            return ret

    else:
        i = 0
        try:
          async for item in g:
              ret.append(item)
              i += 1

              if i == count:
                  raise StopAsyncIteration
        except StopAsyncIteration:
            return ret
        finally:
            return ret