from pathlib import Path
from typing import Literal

"""
为前端的 pages/DynamicComponent 生成导入，以实现多窗口
"""


_NOT_INCLUDED = [
    'DynamicComponent'
]

def read_components():

    comp_dir = Path('src/pages')
    comps = [
        p.stem
        for p in comp_dir.iterdir()
    ]
    [comps.remove(n) for n in _NOT_INCLUDED]

    return comps

def gen_imports(comps: list[str]) -> list[str]:

    lines = [
        f"import {n} from './{n}.vue'"
        for n in comps
    ]

    lines += ['interface componentIndex {[index: string] : any}']

    lines += ['const components: componentIndex = {']

    lines += [
        f'  {n}: {n},'
        for n in comps
    ]

    lines += ['}']

    return lines

def gen_interface(comps: list[str]) -> list[str]:

    lines = [
        'interface AppWindow {',
        '    title?: string;',
        '    component: ' + ' | '.join((f"'{cp}'" for cp in comps)) + ';',
        '    props?: object;',
        '}'
    ]
    return lines

def insert_into_comments(
    filename: str, type: Literal['Import', 'Interface'], lines: list[str]):

    with open(filename, 'r', encoding='utf-8') as rf:
        src = rf.read()

    src_lines = src.split('\n')

    start_lineno = None
    end_lineno = None
    for i, l in enumerate(src_lines):
        if l == f'/** 自动生成 {type} Begin */':
            start_lineno = i
        if l == f'/** 自动生成 {type} End */':
            end_lineno = i

    assert start_lineno is not None
    assert end_lineno is not None

    src_lines = src_lines[:start_lineno+1] + lines + src_lines[end_lineno:]

    with open(filename, 'w', encoding='utf-8') as wf:
        wf.write('\n'.join(src_lines))

if __name__ == '__main__':
    IMPORT_TARGET_FILE = 'src/pages/DynamicComponent.vue'
    INTERFACE_TARGET_FILE = 'src/plugins/windowManager.ts'

    comps = read_components()

    insert_into_comments(IMPORT_TARGET_FILE, 'Import', gen_imports(comps))
    insert_into_comments(INTERFACE_TARGET_FILE, 'Interface', gen_interface(comps))

