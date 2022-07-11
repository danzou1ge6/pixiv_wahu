

import dataclasses
from datetime import datetime
from pathlib import Path
from typing import Any

from ..http_typing import JSONItem
from .webapi_exceptions import WahuJsonizeablizeFail


def jsonizeablize(inp: Any) -> JSONItem:
    """
    将 Dataclass, Path, datetime, list, tuple, str, int, bool 转换成可以 JSON 化
    的 dict, list, str, int, bool 的组合
    """

    if isinstance(inp, list):
        return [jsonizeablize(item) for item in inp]

    elif isinstance(inp, dict):
        return {key: jsonizeablize(inp[key]) for key in inp.keys()}

    elif isinstance(inp, tuple):
        return [jsonizeablize(item) for item in inp]

    elif isinstance(inp, (str, int, bool, float)):
        return inp

    elif dataclasses.is_dataclass(inp):
        return jsonizeablize(dataclasses.asdict(inp))

    elif inp is None:
        return None

    elif isinstance(inp, Path):
        return str(inp)

    elif isinstance(inp, datetime):
        return inp.strftime('%Y-%m-%d %H:%M:%S')

    else:
        raise WahuJsonizeablizeFail(inp)
