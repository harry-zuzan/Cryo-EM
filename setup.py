from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

import numpy

numpy_inc = numpy.get_include()

extensions = [
    Extension("cryoem.polar_image_ft", ["cryoem/polar_image_ft.pyx"],
        include_dirs = [numpy_inc],
		),
#    Extension("cryoem.polar_image_pcode", ["cryoem/polar_image_pcode.py"]
#		)
	]

setup(
    name = "Cryo-Electron Microscopy Utilities",
    ext_modules = cythonize(extensions),
	packages=['cryoem'],
)
