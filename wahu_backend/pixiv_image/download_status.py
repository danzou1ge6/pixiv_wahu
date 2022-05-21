from dataclasses import dataclass
from inspect import Traceback
from random import sample
from typing import Iterable, Iterator, Literal, Optional
from collections import OrderedDict



@dataclass
class DownloadProgressRaw:
    gid: str
    total_size: int
    downloaded_size: int
    descript: Optional[str]
    status: Literal['inprogress', 'finished', 'error']


class DownloadProgress(DownloadProgressRaw):

    def __init__(
        self, gid: str, url: str,
        total_size: Optional[int]=None, descript: Optional[str]=None
    ):
        self.gid: str = gid
        self.url: str = url
        self.descript: Optional[str] = descript

        self.total_size: Optional[int] = total_size
        self.downloaded_size: int = 0



    def update(self, delta: int) -> None:
        self.downloaded_size += delta

    @property
    def downloaded(self) -> int:
        return self.downloaded_size

    @property
    def downloaded_kb(self) -> str:
        return f'{self.downloaded_size / 1024:.0f}'

    @property
    def downloaded_mb(self) -> str:
        return f'{self.downloaded_size / 1024**2:.2f}'

    @property
    def total(self) -> Optional[int]:
        return self.total_size

    @property
    def total_kb(self) -> str:
        return f'{self.total_size / 1024:.0f}' if self.total_size is not None else 'Unknown'

    @property
    def total_mb(self) -> str:
        return f'{self.total_size / 1024**2:.2f}' if self.total_size is not None else 'Unknown'


    @property
    def percentage(self) -> Optional[float]:

        return self.downloaded_size / self.total_size \
               if self.total_size is not None else None

    @property
    def readable_perct(self) -> str:
        perc = self.percentage
        return f'{perc * 100:.1f}%' if perc is not None else 'Unknown'

    def __enter__(self) -> 'DownloadProgress':
        self.status = 'inprogress'

        return self

    def __exit__(self,
                 excpt_type: Optional[type] = None,
                 excpt_value: Optional[Exception] = None,
                 excpt_tcbk: Optional[Traceback] = None):
        if excpt_value is not None:
            self.status = 'error'
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
        total_size: Optional[str | int],
        descript: Optional[str]=None
    ) -> DownloadProgress:

        gid = _generate_gid(self.download_status_record.keys())

        if total_size is not None:
            total_size = int(total_size)

        nds =  DownloadProgress(gid, url, total_size, descript=descript)

        if len(self.download_status_record) > self.record_size:
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
    def inprogress(self) -> Iterator[DownloadProgress]:
        return (v for v in self.download_status_record.values()
                if v.status == 'inprogress')
