import sqlite3

import pytest
from wahu_backend.file_tracing import FileTracingConfig
from wahu_backend.sqlite_tools.st_exceptions import SqliteTableStoreConfigError
from wahu_backend.sqlite_tools.store_config import ConfigStoredinSqlite


@pytest.fixture(scope='class')
def db_cur():
    con = sqlite3.connect(':memory:')
    cur = con.cursor()

    yield cur

    con.close()


@pytest.fixture(scope='class')
def config_editor(db_cur):
    ce = ConfigStoredinSqlite(FileTracingConfig)
    ce.bind(db_cur)
    return ce


@pytest.fixture(scope='class')
def init_written(config_editor):
    config_editor.create_if_not()
    if config_editor.empty:
        config_editor.insert([FileTracingConfig(123, 'test', [])])


@pytest.mark.usefixtures('init_written')
class TestGetattr:
    @staticmethod
    def test_getter(config_editor):
        ret = config_editor.v.name
        assert ret == 'test'


@pytest.mark.usefixtures('init_written')
class TestSetter:
    @staticmethod
    def test_setter(config_editor, db_cur):
        config_editor.v.name = 'new'

        assert db_cur.execute(
            f'SELECT * FROM {config_editor.name}').fetchone()[1] == 'new'


@pytest.mark.usefixtures('init_written')
def test_set_twice(config_editor):
    with pytest.raises(SqliteTableStoreConfigError):
        config_editor.insert([])
