import argparse

from typing import Optional


class ArgumentParser(argparse.ArgumentParser):

    def exit(self, status: int=0, message: Optional[str]=None) -> None:
        pass

    def error(self, message: str) -> None:
        raise argparse.ArgumentError(None, message)
