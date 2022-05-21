from typing import Optional

from ..wahu_core.wahu_method import WahuMethod
from .cli import WahuMetdodsWithCli


class WahuMethods(WahuMetdodsWithCli):

    @classmethod
    def get(cls, name: str) -> Optional[WahuMethod]:

        try:
            m = getattr(cls, name)
        except AttributeError as ae:
            return None

        return m

