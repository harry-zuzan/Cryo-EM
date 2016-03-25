#!/usr/bin/env python2

# Writes an image file of the real data

from __future__ import print_function

import optparse, sys, os
import subprocess

import numpy, h5py
from PIL import Image

import platform

print('Python version', platform.python_version())

IMAGE_PATH = 'image-power'

GROUP = 'Observed'
FOURIER_DATA_SET = 'fourier image'
IMAGE_NAME_SUFFIX = '-power'


def parse_options():
	usage = "usage: %prog [options] mrc-file"

	parser = optparse.OptionParser(usage=usage)

	# Internal to the parser
	option_group = optparse.OptionGroup(parser,"Options",
		"Command line options")

	option_group.add_option("--group",
		dest='group', default=GROUP,
		help="image group name [default=%default]")

	option_group.add_option("--fourier-data-set",
		dest='fourier-data-set', default=FOURIER_DATA_SET,
		help="Fourier transform data set name [default=%default]")

	option_group.add_option("--image-path",
		dest='image-path', default=IMAGE_PATH,
		help="path to output images [default=%default]")

	option_group.add_option("--image-name-suffix",
		dest='image-name-suffix', default=IMAGE_NAME_SUFFIX,
		help="suffix to the image name before the dot [default=%default]")

	parser.add_option_group(option_group)

	return parser



parser = parse_options()
options,pargs = parser.parse_args()

if not len(pargs):
	parser.print_help()
	sys.exit()


image_path = getattr(options,'image-path')
if image_path[-1] == '/': image_path = image_path[:-1]

if not os.path.exists(image_path):
	status = subprocess.call(['mkdir',image_path])
	if status:
		print('error creating directory', image_path)
		sys.exit()


image_name_suffix = getattr(options,'image-name-suffix')
group = getattr(options,'group')
fourier_data_set = getattr(options,'fourier-data-set')


for hfname in pargs:
	print('processing', hfname)

	if not os.path.isfile(hfname):
		print('Error locating', hfname)
		sys.exit()

	try: hfile = h5py.File(hfname,)
	except:
		print('Error opening', hfname)
		sys.exit()

	try: data_grp = hfile[group]
	except:
		err_str = 'Error finding HDF group {} in {}'.format(group, hfname)
		print(err_str)
		print('closing', hfname)
		hfile.close()
		print('Exiting', sys.argv[0])
		sys.exit()

	try: freq_dset = data_grp[fourier_data_set]
	except:
		err_fmt_str = 'Error finding dataset {} in HDF group {}'
		err_str = err_fmt_str.format(fourier_data_set, group)
		print(err_str)
		print('closing', hfname)
		hfile.close()
		print('Exiting', sys.argv[0])
		sys.exit()

	freq_image = freq_dset[:]

	hfile.close()

	power_image = numpy.abs(freq_image)**2

	power_image -= power_image.min()

	power_image[0,0] = 0.0
	power_image *= 255.0/power_image.max()

	power_image = numpy.roll(power_image,power_image.shape[0]/2,axis=0)
	power_image = numpy.roll(power_image,power_image.shape[1]/2,axis=1)

	power_image255 = power_image.copy().astype(numpy.uint8)

	I = Image.fromarray(power_image255)

	iname = hfname.split('/')[-1][:-5]
	pname = '{0}/{1}{2}.{3}'.format(image_path,iname,image_name_suffix,'png')

	I.save(pname)

