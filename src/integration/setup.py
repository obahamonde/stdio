from Cython.Build import cythonize
from setuptools import Extension, setup

ext_modules = [
    Extension(
        "rocksdb",
        sources=["rocksdb.pyx"],
        include_dirs=["/usr/local/include"],
        library_dirs=["/usr/local/lib"],
        libraries=["rocksdb"],
        extra_compile_args=["-std=c++17"],  # Add this line
        language="c++",
    )
]

setup(
    name="rocksdb",
    ext_modules=cythonize(ext_modules),
)
