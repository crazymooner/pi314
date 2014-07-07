#!/usr/bin/env python

"""
setup.py file for SWIG example
"""

from distutils.core import setup, Extension


MdApi_module = Extension('_MdApi',
                          sources=['MdApi_wrap.cxx'],
			  runtime_library_dirs=["$ORIGIN/"],
                          extra_objects = ["thostmduserapi.so", "thosttraderapi.so"],
)

setup (name = 'MdApi',
       version = '0.1',
       author      = "tliu",
       description = """Python wrapper for CTP""",
       ext_modules = [MdApi_module],
       py_modules = ["MdApi"],
       )
