from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from wahu_backend.file_tracing import FileEntry, FileTracer
from wahu_backend.file_tracing.file_tracer import DEFAULT_IGNORE_LIST


class DabataseContextManager:
    def __init__(self, dd):
        self.dd = dd

    def __enter__(self):
        self.dd.connect()
        return self.dd

    def __exit__(self, a, b, c):
        self.dd.close()


@pytest.fixture(scope='class')
def tmp_dir_path():
    with TemporaryDirectory() as td:
        tdp = Path(td)
        (tdp / 'a').touch()
        (tdp / 'b').touch()
        yield tdp
    return


@pytest.fixture(scope='class')
def file_entries():
    fe1 = FileEntry(Path('a'), '1')
    fe2 = FileEntry(Path('b'), '2')
    return fe1, fe2


@pytest.fixture(scope='class')
def file_tracer_provider(tmp_dir_path):
    ft = FileTracer('test', tmp_dir_path)
    ftp = DabataseContextManager(ft)
    return ftp


class TestCfg:

    @staticmethod
    def test_init_config(file_tracer_provider):
        with file_tracer_provider as ft:
            cur = ft.index_con.cursor()
            assert cur.execute('SELECT * FROM config').fetchone()[1] == 'test'

    @staticmethod
    def test_read_config(file_tracer_provider):
        with file_tracer_provider as ft:
            ignore = ft.config.ignore
            assert ignore == DEFAULT_IGNORE_LIST

    @staticmethod
    def test_write_config(file_tracer_provider):
        with file_tracer_provider as ft:
            ft.config.ignore = ['tttt']
            assert ft.config.ignore == ['tttt']

    @staticmethod
    def test_get_config(file_tracer_provider):
        with file_tracer_provider as ft:
            cfg = ft.get_config()
        assert cfg.name == 'test'


class TestScan:

    @staticmethod
    def test_scan_ignore(file_tracer_provider, file_entries):
        with file_tracer_provider as ft:
            ft.config.ignore = [file_entries[0].path.name, 'index.db']
            file_list = ft.scan()
            assert len(file_list) == 1
            assert file_list[0].name == file_entries[1].path.name

    @staticmethod
    def test_scan(file_tracer_provider, file_entries):
        with file_tracer_provider as ft:
            ft.config.ignore = ['index.db']
            file_list = ft.scan()
            fe1, fe2 = file_entries
            assert set([p.name
                        for p in file_list]) == {fe1.path.name, fe2.path.name}


class TestIndex:

    @staticmethod
    def test_add_cache(file_tracer_provider, file_entries):
        with file_tracer_provider as ft:
            ft.add_cache(list(file_entries))
            assert ft.index_con.execute('SELECT * FROM cached WHERE fid=?',
                                        ('1', )).fetchone() != None

    @staticmethod
    def test_update_index(file_tracer_provider, file_entries):
        with file_tracer_provider as ft:
            ft.update_index()

            assert ft.index_con.execute(
                'SELECT * FROM cached WHERE fid=?',
                (file_entries[1].fid, )).fetchone() == None
            assert ft.index_con.execute(
                'SELECT * FROM indexed WHERE fid=?',
                (file_entries[1].fid, )).fetchone() != None


@pytest.fixture(scope='class')
def init_index(file_tracer_provider, file_entries):
    with file_tracer_provider as ft:
        ft.add_cache(list(file_entries))
        ft.update_index()


@pytest.mark.usefixtures('init_index')
class TestValidation:

    @staticmethod
    def test_validate_index(file_tracer_provider, tmp_dir_path, file_entries):
        with file_tracer_provider as ft:
            (tmp_dir_path / file_entries[0].path).unlink()
            invalid_indexs = ft.validate_index()
            assert len(invalid_indexs) == 1
            assert invalid_indexs[0].fid == file_entries[0].fid
            assert invalid_indexs[0].path == file_entries[0].path

    @staticmethod
    def test_valid_files(file_tracer_provider, file_entries):
        with file_tracer_provider as ft:
            ft.remove_index([file_entries[1].fid])
            invalid_files = ft.validate_files()
            assert len(invalid_files) == 1
            assert invalid_files[0].name == file_entries[1].path.name


@pytest.mark.usefixtures('init_index')
class TestCheckout:

    @staticmethod
    def test_checkout(file_tracer_provider, file_entries):
        with file_tracer_provider as ft:
            p1 = ft.checkout(file_entries[0].fid)
            assert p1.name == file_entries[0].path.name
