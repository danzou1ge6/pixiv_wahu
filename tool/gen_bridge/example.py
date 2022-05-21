import dataclasses


from .dataclass2interface import generate_dataclass_ts
from .func2func import generate_func_ts


@dataclasses.dataclass
class DataclassA:
    x: int

@dataclasses.dataclass
class Example:
    a: int
    b: list[str]
    c: DataclassA
    d: list[DataclassA]
    e: tuple[DataclassA, list[tuple[DataclassA]]]

gret = generate_dataclass_ts(DataclassA)
gret += '\n' + generate_dataclass_ts(Example)

def f(m: tuple[list[Example], tuple[Example, str, int]], n: list[Example]) -> tuple[bool, str]:
    return (True, '1')

f_body = """
    return [true, '1'];
"""

gret += generate_func_ts(f, f_body)

with open('example_output.ts', 'w', encoding='utf-8') as wf:
    wf.write(gret)



