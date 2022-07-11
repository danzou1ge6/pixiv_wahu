from libc.stdlib cimport malloc, free
from libc.string cimport memcpy
from libc.math cimport log, exp

from simple_mat cimport _Mat


cdef _Mat* _Mat_new(int rows, int cols):
    cdef _Mat* mat = <_Mat*> malloc(sizeof(_Mat))
    cdef double * data = <double*> malloc(sizeof(double) * rows * cols)

    if mat is NULL or data is NULL:
        return NULL

    mat.data = data
    mat.rows = rows
    mat.cols = cols

    return mat


cdef int _Mat_dot(_Mat *a, _Mat *b, _Mat *ret):
    # 将 a 和 b 点乘，返回一个新的矩阵
    # 如果 a 的列数和 b 的行数不匹配，返回 -1
    # 如果 运算结果和 ret 的大小不匹配，返回 -2

    if a.cols != b.rows:
        return -1

    if a.rows != ret.rows or b.cols != ret.cols:
        return -2

    cdef int i, j, k

    for i in range(ret.rows):
        for j in range(ret.cols):

            ret.data[i * ret.cols + j] = 0

            for k in range(a.cols):
                ret.data[i * ret.cols + j] += a.data[i * a.cols + k] * b.data[k * b.cols + j]
    
    return 0

cdef int _Mat_copy(_Mat* frm, _Mat* to):
    # 复制矩阵
    # 如果大小不匹配，返回 -1

    if frm.rows != to.rows or frm.cols != to.cols:
        return -1
    
    memcpy(to.data, frm.data, sizeof(double) * frm.rows * frm.cols)

    return 0

cdef int _Mat_transpose(_Mat* mat, _Mat* ret):
    # 转置矩阵
    # 如果大小不匹配，返回 -1

    if mat.rows != ret.cols or mat.cols != ret.rows:
        return -1
    
    cdef int i, j
    for i in range(mat.rows):
        for j in range(mat.cols):

            ret.data[j * ret.cols + i] = mat.data[i * mat.cols + j]
    
    return 0

cdef int _Mat_add(_Mat* a, _Mat* b, _Mat* ret):
    # 矩阵相加
    # 如果大小不匹配则返回 -1

    if a.rows != b.rows or a.cols != b.cols or a.rows != ret.rows or a.cols != ret.cols:
        return -1
    
    cdef int i

    for i in range(a.rows * a.cols):
            ret.data[i] = a.data[i] + b.data[i]
    
    return 0

cdef int _Mat_subtract(_Mat* a, _Mat* b, _Mat* ret):
    # 矩阵相减
    # 如果大小不匹配则返回 -1

    if a.rows != b.rows or a.cols != b.cols or a.rows != ret.rows or a.cols != ret.cols:
        return -1
    
    cdef int i

    for i in range(a.rows * a.cols):
            ret.data[i] = a.data[i] - b.data[i]
    
    return 0

cdef int _Mat_add_double(_Mat* mat, double flt, _Mat* ret):
    # 矩阵加上标量
    # 如果大小不匹配返回 -1

    if mat.rows != ret.rows or mat.cols != ret.cols:
        return -1

    cdef int i
    for i in range(mat.rows * mat.cols):
        ret.data[i] = mat.data[i] + flt
    
    return 0

cdef int _Mat_subtract_double(_Mat* mat, double flt, _Mat* ret):
    # 矩阵减去标量
    # 如果大小不匹配返回 -1

    if mat.rows != ret.rows or mat.cols != ret.cols:
        return -1

    cdef int i
    for i in range(mat.rows * mat.cols):
        ret.data[i] = mat.data[i] - flt
    
    return 0

cdef int _Mat_subtractedby_double(_Mat* mat, double flt, _Mat* ret):
    # 标量减去矩阵
    # 如果大小不匹配返回 -1

    if mat.rows != ret.rows or mat.cols != ret.cols:
        return -1

    cdef int i
    for i in range(mat.rows * mat.cols):
        ret.data[i] = flt - mat.data[i]
    
    return 0


cdef int _Mat_scale(_Mat* mat, double scaler, _Mat* ret):
    # 矩阵乘以标量
    # 如果大小不匹配则返回 -1

    if mat.rows != ret.rows or mat.cols != ret.cols:
        return -1

    cdef int i
    for i in range(mat.rows * mat.cols):
        ret.data[i] = mat.data[i] * scaler
    
    return 0

cdef int _Mat_exp(_Mat* mat, _Mat* ret):
    # 将矩阵中所有元素输入自然指数函数
    # 如果 mat 和 ret 大小不匹配，返回 -1

    if mat.rows != ret.rows or mat.cols != ret.cols:
        return -1

    cdef int i
    for i in range(mat.rows * mat.cols):
        ret.data[i] = exp(mat.data[i])
    
    return 0

cdef int _Mat_log(_Mat* mat, _Mat* ret):
    # 将矩阵中所有元素取自然对数
    # 如果 mat 和 ret 大小不匹配，返回 -1

    if mat.rows != ret.rows or mat.cols != ret.cols:
        return -1

    cdef int i
    for i in range(mat.rows * mat.cols):
        ret.data[i] = log(mat.data[i])
    
    return 0

cdef int _Mat_mul(_Mat* a, _Mat* b, _Mat* ret):
    # 矩阵元素积
    # 如果大小不匹配则返回 -1

    if a.rows != b.rows or a.cols != b.cols or a.rows != ret.rows or a.cols != ret.cols:
        return -1
    
    cdef int i

    for i in range(a.rows * a.cols):
            ret.data[i] = a.data[i] * b.data[i]
    
    return 0

cdef int _Mat_div(_Mat* a, _Mat* b, _Mat* ret):
    # 矩阵元素相除
    # 如果大小不匹配则返回 -1

    if a.rows != b.rows or a.cols != b.cols or a.rows != ret.rows or a.cols != ret.cols:
        return -1
    
    cdef int i

    for i in range(a.rows * a.cols):
            ret.data[i] = a.data[i] / b.data[i]
    
    return 0

cdef int _Mat_divedby_double(_Mat* mat, double scaler, _Mat* ret):
    # double 被矩阵除
    # 如果大小不匹配则返回 -1

    if mat.rows != ret.rows or mat.cols != ret.cols:
        return -1

    cdef int i
    for i in range(mat.rows * mat.cols):
        ret.data[i] = scaler / mat.data[i]
    
    return 0

cdef int _Mat_average(_Mat* mat, int axis, _Mat* ret):
    # 矩阵在 axis 上取平均
    # 如果 mat 和 ret 大小不匹配，返回 -1
    # 如果 axis 不为 1 或 2 ，返回 -2

    cdef int i, j
    cdef double s

    if axis == 1:  # 返回 dim1: 1 dim2: cols

        if ret.rows != 1 or ret.cols != mat.cols:
            return -1

        for j in range(mat.cols):

            s = 0
            for i in range(mat.rows):
                s += mat.data[i * mat.cols + j]
            
            ret.data[j] = s / mat.rows
    
    elif axis == 2:  # 返回 dim1: rows dim2: 1

        if ret.rows != mat.rows or ret.rows != 1:
            return -1

        for i in range(mat.rows):

            s = 0
            for j in range(mat.cols):
                s += mat.data[i * mat.cols + j]
            
            ret.data[i] = s / mat.cols
        
    else:
        return -2
    
    return 0


cdef class Mat:

    def __cinit__(self, lst=None):
        # 如果传入了 lst ，则根据此二维 list 初始化
        # 否则将 _mat 初始化为空指针

        self._mat = NULL

        cdef int rows, cols

        if lst is not None:
            rows = len(lst)
            cols = len(lst[0])

            self._mat = _Mat_new(rows, cols)

            if self._mat is NULL:
                raise MemoryError()
    
            self._mat.rows = rows
            self._mat.cols = cols

            for i, row in enumerate(lst):
                for j, item in enumerate(row):
                    self._mat.data[i * cols + j] = item
    
    def __dealloc__(self):
        if self._mat is not NULL:
            free(self._mat)
    
    @property
    def rows(self):
        return self._mat.rows
    
    @property
    def cols(self):
        return self._mat.cols
    
    def as_list(self):
        return [
            [self._mat.data[i * self._mat.cols + j] for j in range(self._mat.cols)]
            for i in range(self._mat.rows)
        ]

    @staticmethod
    cdef _from_pointer(_Mat* _mat):
        # 从 _Mat 的指针构造一个 Mat

        mat = Mat()
        mat._mat = _mat
        return mat
    
    @staticmethod
    cdef _Mat* _new__mat(int rows, int cols):
        # 创建一个新的 _Mat
        # 如果内存不足，抛出 MemoryError

        cdef _Mat *_new = _Mat_new(rows, cols)
        if _new is NULL:
            raise MemoryError()
        return _new
        
    def dot(self, Mat other):
        # 点乘另一个矩阵

        cdef _Mat *_ret = Mat._new__mat(self._mat.rows, other._mat.cols)

        cdef int ret_code = _Mat_dot(self._mat, other._mat, _ret)

        if ret_code == -1:
            raise ValueError(f'a.cols ({self._mat.cols}) 不匹配 b.rows ({other._mat.rows})')

        return Mat._from_pointer(_ret)
    
    def copy(self):
        # 复制此矩阵

        cdef _Mat *_new = Mat._new__mat(self._mat.rows, self._mat.cols)

        _Mat_copy(self._mat, _new)
        
        return Mat._from_pointer(_new)
    
    def __str__(self):
        return str(self.as_list())
    
    @property
    def T(self):
        # 返回一个新的矩阵，是此矩阵的转置

        cdef _Mat *_tps = Mat._new__mat(self._mat.cols, self._mat.rows)

        _Mat_transpose(self._mat, _tps)
        
        return Mat._from_pointer(_tps)
    
    def add(self, Mat other):
        cdef _Mat *_ret = Mat._new__mat(self._mat.rows, self._mat.cols)

        cdef int ret_code = _Mat_add(self._mat, other._mat, _ret)
        if ret_code == -1:
            raise ValueError('a 和 b 的大小不匹配')

        return Mat._from_pointer(_ret)
    
    def subtract(self, Mat other):
        cdef _Mat *_ret = Mat._new__mat(self._mat.rows, self._mat.cols)

        cdef int ret_code = _Mat_subtract(self._mat, other._mat, _ret)
        if ret_code == -1:
            raise ValueError('a 和 b 的大小不匹配')

        return Mat._from_pointer(_ret)
    
    def add_double(self, double scaler):
        cdef _Mat *_ret = Mat._new__mat(self._mat.rows, self._mat.cols)

        _Mat_add_double(self._mat, scaler, _ret)

        return Mat._from_pointer(_ret)

    def subtract_double(self, double scaler):
        cdef _Mat *_ret = Mat._new__mat(self._mat.rows, self._mat.cols)

        _Mat_subtract_double(self._mat, scaler, _ret)

        return Mat._from_pointer(_ret)
    
    def subtractedby_double(self, double scaler):
        cdef _Mat *_ret = Mat._new__mat(self._mat.rows, self._mat.cols)

        _Mat_subtractedby_double(self._mat, scaler, _ret)

        return Mat._from_pointer(_ret)
    
    def scale(self, double scaler):
        cdef _Mat *_ret = Mat._new__mat(self._mat.rows, self._mat.cols)

        _Mat_scale(self._mat, scaler, _ret)

        return Mat._from_pointer(_ret)
    
    def mul(self, Mat other):
        cdef _Mat *_ret = Mat._new__mat(self._mat.rows, self._mat.cols)

        _Mat_mul(self._mat, other._mat, _ret)

        return Mat._from_pointer(_ret)
    
    def div(self, Mat other):
        cdef _Mat *_ret = Mat._new__mat(self._mat.rows, self._mat.cols)

        _Mat_div(self._mat, other._mat, _ret)

        return Mat._from_pointer(_ret)
    
    def divedby_double(self, double scaler):
        cdef _Mat *_ret = Mat._new__mat(self._mat.rows, self._mat.cols)

        _Mat_divedby_double(self._mat, scaler, _ret)

        return Mat._from_pointer(_ret)
    
    def average(self, axis=1):
        cdef _Mat *_ret

        if axis == 1:
            _ret = Mat._new__mat(1, self._mat.cols)
        elif axis == 2:
            _ret = Mat._new__mat(self._mat.rows, 1)
        else:
            raise ValueError('axis 只能为 1 或 2')
        
        _Mat_average(self._mat, axis, _ret)

        return Mat._from_pointer(_ret)
        
    def __add__(self, other):
        if isinstance(other, Mat):
            return self.add(other)
        elif isinstance(other, float):
            return self.add_double(other)
        else:
            raise TypeError('只能加上 float / Mat')

    def __sub__(self, other):
        if isinstance(other, Mat):
            if isinstance(self, Mat):
                return self.subtract(other)
            elif isinstance(self, float):
                return other.subtractedby_double(self)
            else:
                raise TypeError('只能被 float / Mat 减')
        
        elif isinstance(other, float):
            return self.subtract_double(other)
        else:
            raise TypeError('只能减去 float / Mat')
    
    
    def __mul__(self, other):
        if isinstance(other, float):
            return self.scale(other)
        elif isinstance(other, Mat):
            return self.mul(other)
        else:
            raise TypeError('只能乘以 float / Mat')
    
    def __truediv__(self, other):
        if isinstance(other, float):
            return self.scale(1 / other)

        elif isinstance(other, Mat):
            if isinstance(self, Mat):
                return self.div(other)
            elif isinstance(self, float):
                return other.divedby_double(self)
            else:
                raise TypeError('只能被 float / Mat 除')
                
        else:
            raise TypeError('只能乘以 float / Mat')
    
    def __getitem__(self, idx):
        i, j = idx

        if i >= self._mat.rows:
            raise IndexError(f'矩阵仅有 {self._mat.rows} 列')
        if j >= self._mat.cols:
            raise IndexError(f'矩阵仅有 {self._mat.cols} 列')

        return self._mat.data[i * self._mat.cols + j]


def many(int rows, int cols, double val):
    cdef _Mat *_new = Mat._new__mat(rows, cols)

    cdef int i
    for i in range(rows * cols):
        _new.data[i] = val
    
    return Mat._from_pointer(_new)


def exp_mat(Mat mat):
    cdef _Mat *_ret = Mat._new__mat(mat._mat.rows, mat._mat.cols)

    _Mat_exp(mat._mat, _ret)

    return Mat._from_pointer(_ret)


def log_mat(Mat mat):
    cdef _Mat *_ret = Mat._new__mat(mat._mat.rows, mat._mat.cols)

    _Mat_log(mat._mat, _ret)

    return Mat._from_pointer(_ret)
