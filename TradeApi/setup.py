#!/usr/bin/env python

"""
setup.py file for SWIG example
"""

from distutils.core import setup, Extension


TraderApi_module = Extension('_TraderApi',
                          sources=['TraderApi_wrap.cxx'],
			  runtime_library_dirs=["$ORIGIN/"],
                          extra_objects = ["thostmduserapi.so", "thosttraderapi.so"],
)

setup (name = 'TraderApi',
       version = '0.1',
       author      = "tliu",
       description = """Python wrapper for CTP""",
       ext_modules = [TraderApi_module],
       py_modules = ["TraderApi"],
       )
