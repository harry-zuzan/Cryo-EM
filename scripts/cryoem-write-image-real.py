#!/usr/bin/env python2

# Writes an image file of the real data

from __future__ import print_function

import optparse, sys, os
import subprocess

import numpy, h5py
from PIL import Image

import platform

print('Python version', platform.python_version())

IMAGE_PATH = 'image-real'

GROUP = 'Observed'
SPATIAL_DATA_SET = 'real image'
IMAGE_NAME_SUFFIX = '-real'
CLIP=0.0

def parse_options():
	usage = "usage: %prog [options] mrc-file"

	parser = optparse.OptionParser(usage=usage)

	# Internal to the parser
	option_group = optparse.OptionGroup(parser,"Options",
		"Command line options")

	option_group.add_option("--group",
		dest='group', default=GROUP,
		help="image group name [default=%default]")

	option_group.add_option("--spatial-data-set",
		dest='spatial-data-set', default=SPATIAL_DATA_SET,
		help="spatial image data set name [default=%default]")

	option_group.add_option("--image-path",
		dest='image-path', default=IMAGE_PATH,
		help="path to output images [default=%default]")

	option_group.add_option("--image-name-suffix",
		dest='image-name-suffix', default=IMAGE_NAME_SUFFIX,
		help="suffix to the image name before the dot [default=%default]")

	option_group.add_option("--clip",
		 dest='clip', type="float",  default=CLIP,
		help="fraction of extreme intensities to clip [default=%default]")

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
spatial_data_set = getattr(options,'spatial-data-set')
clip = getattr(options,'clip')


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

	try: real_dset = data_grp[spatial_data_set]
	except:
		err_fmt_str = 'Error finding dataset {} in HDF group {}'
		err_str = err_fmt_str.format(spatial_data_set, group)
		print(err_str)
		print('closing', hfname)
		hfile.close()
		print('Exiting', sys.argv[0])
		sys.exit()

	real_image = real_dset[:].astype(numpy.float)

	hfile.close()

	real_image -= real_image.min()

	npix = real_image.shape[0]*real_image.shape[1]
	clip_idx = int(clip*npix)

	sorted_image = numpy.sort(real_image.flat)
	minval,maxval = sorted_image[clip_idx], sorted_image[npix - clip_idx - 1]

	real_image = real_image.clip(minval,maxval)
	real_image *= 255.0/real_image.max()

	real_image255 = real_image.astype(numpy.uint8)

	I = Image.fromarray(real_image255)

	iname = hfname.split('/')[-1][:-5]
	pname = '{0}/{1}{2}.{3}'.format(image_path,iname,image_name_suffix,'png')

	I.save(pname)

