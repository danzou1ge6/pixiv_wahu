from typing import AsyncIterable, Optional
from wahu_backend.aiopixivpy.datastructure_illust import IllustDetail

from wahu_backend.wahu_core.wahu_cli import AsyncGenPipe

async def alist_illusts_piped(
    g: AsyncIterable[list[IllustDetail]],
    pipe: AsyncGenPipe,
    count: int = -1)-> list[list[IllustDetail]]:
    """
    将一个 `AsyncIterable` 中元素提取到一个 `list` 中
    - `:param count:` 提取的最大元素数量, -1 表示耗尽
    """

    ret = []

    if count is -1:
        try:
            async for item in g:
                ret.append(item)
                pipe.output('\n'.join([f"{ilst.title} - {ilst.iid}" for ilst in item]))
        except StopAsyncIteration:
            pass
        finally:
            pipe.close()
            return ret

    else:
        i = 0
        try:
          async for item in g:
                ret.append(item)

                if pipe != None:
                    pipe.output('\n'.join([f"{ilst.title} - {ilst.iid}" for ilst in item]))

                i += 1
                if i == count:
                    raise StopAsyncIteration
        except StopAsyncIteration:
            pass
        finally:
            pipe.close()
            return ret
