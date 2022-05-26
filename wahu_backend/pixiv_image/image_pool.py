from typing import Optional, OrderedDict
from .image_getter import PixivImageGetter


class PixivImagePool(PixivImageGetter):
    """获取图片后缓存图片"""

    def __init__(
        self,
        host: Optional[str] = None,
        size: int = 100,
        timeout: float = 5.0,
        chunk: int = 2048,
        connection_limit: int = 7,
        num_parallel: int = 2,
        record_size: int = 100
    ) -> None:

        self.size = size
        self.pool: OrderedDict[str, bytes] = OrderedDict()
        super().__init__(
            host, timeout, chunk,
            connection_limit=connection_limit,
            num_parallel=num_parallel,
            record_size=record_size
        )

    async def get_image(self, file_path: str
                       , descript: Optional[str] = None) -> bytes:

        if file_path in self.pool.keys():
            return self.pool[file_path]

        img = await super().get_image(file_path, descript=descript)

        if len(self.pool) >= self.size:
            self.pool.popitem(last=False)

        self.pool[file_path] = img

        return img

