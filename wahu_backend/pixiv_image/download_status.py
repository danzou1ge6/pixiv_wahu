from dataclasses import dataclass
from inspect import Traceback
from random import sample
from typing import Iterable, Iterator, Literal, Optional
from collections import OrderedDict



@dataclass(slots=True)
class DownloadProgressRaw:
    gid: str
    total_size: Optional[int]
    downloaded_size: int
    descript: Optional[str]
    status: Literal['inprogress', 'finished', 'error', 'pending']


class DownloadProgress(DownloadProgressRaw):

    __slots__ = ('url')

    def __init__(
        self,
        gid: str,
        url: str,
        descript: Optional[str]=None
    ):
        self.gid = gid
        self.url = url
        self.descript = descript
        self.total_size = None
        self.downloaded_size = 0

    def start(self, total_size: Optional[int | str]) -> None:

        if total_size is not None:
            total_size = int(total_size)

        self.total_size = total_size
        self.status = 'inprogress'

    def update(self, delta: int) -> None:
        self.downloaded_size += delta

    @property
    def total_kb(self):
        if self.total_size is None:
            return ''
        else:
            return f'{self.total_size / 1024:.0f}kb'

    @property
    def downloaded_kb(self):
        return f'{self.downloaded_size / 1024:.0f}kb'


    def __enter__(self) -> 'DownloadProgress':
        self.status = 'pending'

        return self

    def __exit__(self,
                 excpt_type: Optional[type] = None,
                 excpt_value: Optional[Exception] = None,
                 excpt_tcbk: Optional[Traceback] = None):
        if excpt_value is not None:
            self.status = 'error'
            raise excpt_value
        else:
            self.status = 'finished'


def _generate_gid(not_in: Iterable) -> str:

    while True:
        n = ''.join(sample('abcdefghijklmnopqrstuvwxyz0123456789', 8))

        if n not in not_in:
            break

    return n



class DownloadProgressTracker:
    """跟踪下载进程"""

    def __init__(self, record_size: int = 100):

        self.download_status_record: OrderedDict[str, DownloadProgress] = OrderedDict()
        self.record_size = record_size

    def new(
        self, url: str,
        descript: Optional[str]=None
    ) -> DownloadProgress:
        """descrip 一般使用下载路径"""

        gid = _generate_gid(self.download_status_record.keys())

        nds =  DownloadProgress(gid, url, descript=descript)

        if len(self.download_status_record) >= self.record_size:
            self.download_status_record.popitem(last=False)

        self.download_status_record[gid] = nds

        return nds

    def __getitem__(self, gid: str):
        return self.download_status_record.get(gid, None)

    def __iter__(self) -> Iterator[DownloadProgress]:
        return (v for v in self.download_status_record.values())

    def __len__(self) -> int:
        return len(self.download_status_record.keys())

    @property
    def finished(self) -> Iterator[DownloadProgress]:
        return (v for v in self.download_status_record.values()
                if v.status == 'finished')

    @property
    def pending(self) -> Iterator[DownloadProgress]:
        return (v for v in self.download_status_record.values()
                if v.status == 'pending')

    @property
    def inprogress(self) -> Iterator[DownloadProgress]:
        return (v for v in self.download_status_record.values()
                if v.status == 'inprogress')
