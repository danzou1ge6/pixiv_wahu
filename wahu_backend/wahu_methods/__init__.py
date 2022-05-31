from functools import partial
from typing import Callable, Optional, Any

from ..wahu_core import WahuContext, WahuArguments

from .cli import WahuMetdodsWithCli


class WahuMethods(WahuMetdodsWithCli):

    @classmethod
    def get(cls, name: str) -> Optional[Callable[[WahuArguments, WahuContext], Any]]:

        try:
            m = getattr(cls, name)

        except AttributeError:
            return None

        return partial(m.call, cls)

