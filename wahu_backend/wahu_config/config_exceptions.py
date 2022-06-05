from pathlib import Path


class ConfigLoadError(Exception):
    pass

class ConfigLoadKeyError(ConfigLoadError, KeyError):
    def __init__(self, k: str):
        self.k = k

    def __str__(self) -> str:
        return f'在配置中找不到键值 {self.k}'

class ConfigLoadBadPath(ConfigLoadError):
    def __init__(self, p: Path | str):
        self.p = p

    def __str__(self) -> str:
        return f'路径 {self.p} 错误'
