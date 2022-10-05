from typing import Any, Optional


RAW_TYPES = {int, str, bool, float, type(None), Any}

RAW_TYPES_STR = {rt.__name__ for rt in RAW_TYPES}


class Py2TsConvertionError(Exception):

    def __init__(self, expl: str):
        self.expl = expl

    def __str__(self) -> str:
        return self.expl

class PyAnnoType:

    RAW_TYPES_MAPPING = {
        'int': 'number',
        'str': 'string',
        'bool': 'boolean',
        'float': 'number',
        'NoneType': 'null',
        'Any': 'any'
    }

    def __init__(self, tp: str, args: Optional[list['PyAnnoType']]=None):
        if (tp in {'list', 'Iterable', 'Optional', 'Union', 'tuple', 'Literal'}) and args is None:
            raise Py2TsConvertionError(f'{tp} 需要 args')

        self.tp = tp
        self.args = args

    @property
    def ts(self) -> str:
        if self.tp in RAW_TYPES_STR:
            return self.RAW_TYPES_MAPPING[self.tp]

        if self.tp == 'list':
            assert self.args is not None
            return f'Array<{self.args[0].ts}>'

        if self.tp == 'Iterator':
            assert self.args is not None
            return f'Iterator<{self.args[0].ts}>'

        if self.tp == 'AsyncGenerator':
            assert self.args is not None
            return f'AsyncGenerator<{self.args[0].ts}, undefined, {self.args[1].ts}>'

        if self.tp == 'Optional':
            assert self.args is not None
            return f'null | {self.args[0].ts}'

        if self.tp == 'tuple':
            assert self.args is not None
            return '[' + ', '.join((tp.ts for tp in self.args)) + ']'

        if self.tp == 'Literal':
            assert self.args is not None
            return ' | '.join((f"'{litr.tp}'" for litr in self.args))

        if self.tp == 'Union':
            assert self.args is not None
            return ' | '.join((tp.ts for tp in self.args))

        else:
            # dataclass 或者 Any
            return self.tp


class PyAnndVar:

    def __init__(self, name: str, anno_tp: PyAnnoType):
        self.name = name
        self.anno_tp = anno_tp

    @property
    def ts(self) -> str:
        return self.name + ': ' + self.anno_tp.ts
