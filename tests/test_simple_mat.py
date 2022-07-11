from wahu_backend.logistic_regression import simple_mat  # type: ignore[import]
import pytest

import math

@pytest.fixture
def m():
    return simple_mat.Mat(lst=[[1, 2], [3, 4]])


def test_init():
    m = simple_mat.Mat(lst=[[1, 2], [3, 4]])

def test_aslist(m):
    assert m.as_list() == [[1.0, 2.0], [3.0, 4.0]]

def test_dot(m):
    m2 = simple_mat.Mat(lst=[[2], [3]])
    r = m.dot(m2)
    assert r.as_list() == [[8.0], [18.0]]

def test_transpose(m):
    assert m.T.as_list() == [[1.0, 3.0], [2.0, 4.0]]

def test_add(m):
    assert (m + m).as_list() == [[2.0, 4.0], [6.0, 8.0]]

def test_add_float(m):
    assert (m + 1.).as_list() == [[2.0, 3.0], [4.0, 5.0]]

def test_sub_float(m):
    assert (m - 1.).as_list() == [[.0, 1.0], [2.0, 3.0]]

def test_rsub_float(m):
    assert (1. - m).as_list() == [[0.0, -1.0], [-2.0, -3.0]]

def test_subtract(m):
    assert (m - m).as_list() == [[0.0, 0.0], [.0, .0]]

def test_many():
    m = simple_mat.many(1, 2, 1)
    assert m.as_list() == [[1.0, 1.0]]

def test_scale(m):
    assert (m * 2.0).as_list() == [[2.0, 4.0], [6.0, 8.0]]

def test_exp(m):
    assert simple_mat.exp_mat(m).as_list()[0][0] - math.e < 1e-5

def test_log(m):
    assert simple_mat.log_mat(m).as_list()[0][0] < 1e-5

def test_mul(m):
    assert (m * m).as_list() == [[1.0, 4.0], [9.0, 16.0]]

def test_div_mat(m):
    assert (m / m).as_list() == [[1.0, 1.0], [1.0, 1.0]]

def test_divedby_float(m):
    assert (24. / m).as_list() == [[24.0, 12.0], [8.0, 6.0]]

def test_get(m):
    assert m[(0, 0)] == 1.0

def test_average(m):
    ave = m.average(axis=1)
    assert ave.rows == 1 and ave.cols == 2
    assert ave.as_list() == [[2.0, 3.0]]

