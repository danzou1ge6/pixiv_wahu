from setuptools import Extension, setup
from Cython.Build import cythonize
from Cython.Distutils import build_ext


setup(
    name='pixiv_wahu',
    version='0.3.0',
    python_requires='>=3.10',
    ext_modules=cythonize(
        [
            Extension(
                'wahu_backend.logistic_regression.simple_mat',
                [
                    './wahu_backend/logistic_regression/simple_mat.pyx',
                    './wahu_backend/logistic_regression/simple_mat.pxd'
                ])
        ],

    ),
    cmdclass={
        'build_ext': build_ext
    }
)
