from distutils.core import setup
import py2exe
 
setup(console=['main.py'], py_modules=['main'], data_file=['attribute_filter.json'])