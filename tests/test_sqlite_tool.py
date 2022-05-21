import sqlite3

import pytest
from wahu_backend.aiopixivpy.datastructure_illust import IllustDetail
from wahu_backend.sqlite_tools.table_editor import SqliteTableEditor


@pytest.fixture(scope='class')
def db_cur():
    con = sqlite3.connect(':memory:')
    cur = con.cursor()

    yield cur

    con.close()


@pytest.fixture(scope='class')
def editor(db_cur):
    te = SqliteTableEditor('illustDetail', IllustDetail)
    te.bind(db_cur)
    return te


class TestCreate:
    @staticmethod
    def test_create(editor, db_cur):
        editor.create()

        assert db_cur.execute("SELECT name FROM sqlite_master "
                              f"WHERE type='table' AND name='{editor.name}'").fetchone() != None

    @staticmethod
    def test_lazy_create(editor):
        assert editor.has_created() == True


class TestInsert:
    @staticmethod
    def test_insert(editor, db_cur, illust_detail):
        editor.create_if_not()

        editor.insert([illust_detail])

        assert db_cur.execute('SELECT * FROM illustDetail WHERE iid=?',
                              (illust_detail.iid,)).fetchone() != None

    @staticmethod
    def test_insert_twice(editor, db_cur, illust_detail):
        editor.create_if_not()

        editor.insert([illust_detail])
        editor.insert([illust_detail])

        ret = db_cur.execute('SELECT * FROM illustDetail WHERE iid=?',
                             (illust_detail.iid,)).fetchall()
        assert len(ret) == 1


@pytest.fixture(scope='class')
def init_written_table(editor, illust_detail):
    editor.create_if_not()
    editor.insert([illust_detail])


@pytest.mark.usefixtures('init_written_table')
class TestSelect:

    @staticmethod
    def test_select_all(editor, illust_detail):

        ret = editor.select()
        assert ret[0].iid == illust_detail.iid

    @staticmethod
    def test_select_one(editor, illust_detail):

        ret = editor.select(illust_detail.iid)
        assert ret[0].iid == illust_detail.iid

    @staticmethod
    def test_select_where(editor, illust_detail):

        ret = editor.select(iid=illust_detail.iid)
        assert ret[0].iid == illust_detail.iid

    @staticmethod
    def test_select_colunm_all(editor, illust_detail):

        ret = editor.select_cols(cols=['title'])
        assert ret[0][0] == illust_detail.title

    @staticmethod
    def test_select_column(editor, illust_detail):

        ret = editor.select_cols(illust_detail.iid, cols=['title'])
        assert ret[0][0] == illust_detail.title


@pytest.mark.usefixtures('init_written_table')
class TestDelete:

    @staticmethod
    def test_delete_one(editor, illust_detail, db_cur):
        editor.delete([illust_detail.iid])

        assert db_cur.execute('SELECT * FROM illustDetail WHERE iid=?',
                              (illust_detail.iid,)).fetchone() is None

    @staticmethod
    def test_delete_all(editor, db_cur):
        editor.delete()

        assert db_cur.execute('SELECT * FROM illustDetail').fetchall() == []


@pytest.mark.usefixtures('init_written_table')
class TestUpdate:

    @staticmethod
    def test_update_one(editor, db_cur, illust_detail):
        editor.update(illust_detail.iid, title='123')

        assert db_cur.execute('SELECT * FROM illustDetail WHERE title=?',
                              (illust_detail.title,)).fetchone() == None
        assert db_cur.execute('SELECT * FROM illustDetail WHERE title=?',
                              ('123',)).fetchone() != None

    @staticmethod
    def test_update_all(editor, db_cur):
        editor.update(title='123')

        assert db_cur.execute('SELECT * FROM illustDetail WHERE title=?',
                              ('123',)).fetchone() != None
