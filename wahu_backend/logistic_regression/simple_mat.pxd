cdef struct _Mat:
    #  单精度小数的矩阵
    #
    #  data 在内存中的顺序：
    #  [[1, 2, 3],
    #   [4, 5, 6],
    #   [7, 8, 9]]

    int rows
    int cols
    double *data


cdef _Mat* _Mat_new(int rows, int cols)
cdef int _Mat_dot(_Mat *a, _Mat *b, _Mat *ret)
cdef int _Mat_copy(_Mat* frm, _Mat* to)
cdef int _Mat_transpose(_Mat* mat, _Mat* ret)
cdef int _Mat_add(_Mat* a, _Mat* b, _Mat* ret)
cdef int _Mat_add_double(_Mat* mat, double flt, _Mat* ret)
cdef int _Mat_subtract(_Mat* a, _Mat* b, _Mat* ret)
cdef int _Mat_subtract_double(_Mat* mat, double flt, _Mat* ret)
cdef int _Mat_subtractedby_double(_Mat* mat, double flt, _Mat* ret)
cdef int _Mat_scale(_Mat* mat, double scaler, _Mat* ret)
cdef int _Mat_exp(_Mat* mat, _Mat* ret)
cdef int _Mat_log(_Mat* mat, _Mat* ret)
cdef int _Mat_mul(_Mat* a, _Mat* b, _Mat* ret)
cdef int _Mat_div(_Mat* a, _Mat* b, _Mat* ret)
cdef int _Mat_divedby_double(_Mat* mat, double scaler, _Mat* ret)

cdef class Mat:
    cdef _Mat* _mat
    @staticmethod
    cdef _from_pointer(_Mat* _mat)
    @staticmethod
    cdef _Mat* _new__mat(int rows, int cols)
