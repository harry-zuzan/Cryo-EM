#!/usr/bin/env python2

# Writes the power spectrum in polar coordinates

from __future__ import print_function

import optparse, sys, os
import subprocess

import numpy, h5py

import platform
print('Python version', platform.python_version())

import cryoem


# defaults for file access

GROUP = 'Observed'
FOURIER_DATA_SET = 'fourier image'
POLAR_DATA_SET = 'polar fourier image'


# defaults for the polar creating coordinate array

POLAR_ROWS = 256
POLAR_COLS = 128

POLAR_RADIUS = 0.85

RADIUS_SAMPLES = 8
ROTATION_SAMPLES = 8

#------------------------------------------------------`

def parse_options():
	usage = "usage: %prog [options] hdf5 data files"

	parser = optparse.OptionParser(usage=usage)

	# Internal to the parser
	file_option_group = optparse.OptionGroup(parser,"File Access",
		"Where to access input and store oputput in hdf data files")

	file_option_group.add_option("--group",
		dest='group', default=GROUP,
		help="image group name [default=%default]")

	file_option_group.add_option("--fourier-data-set",
		dest='fourier-data-set', default=FOURIER_DATA_SET,
		help="input fourier image data set name [default=%default]")

	file_option_group.add_option("--polar-data-set",
		dest='polar-data-set', default=POLAR_DATA_SET,
		help="output polar image data set name [default=%default]")

	parser.add_option_group(file_option_group)

	transformation_option_group = optparse.OptionGroup(parser,
		"Transformation Options",
		"how to transform to polar coordinates")

	transformation_option_group.add_option("--polar-rows",
		dest='polar-rows', type="int",  default=POLAR_ROWS,
		help="number of rows in the polar representation [default=%default]")

	transformation_option_group.add_option("--polar-cols",
		dest='polar-cols', type="int",  default=POLAR_COLS,
		help="number of columns in the polar representation [default=%default]")

	transformation_option_group.add_option("--polar-radius",
		dest='polar-radius', type="float",  default=POLAR_RADIUS,
		help="radius [0,1] from which to sample pixels [default=%default]")

	transformation_option_group.add_option("--radius-samples",
		dest='radius-samples', type="int",  default=RADIUS_SAMPLES,
		help="radial samples for each polar pixel [default=%default]")

	transformation_option_group.add_option("--rotation-samples",
		dest='rotation-samples', type="int",  default=ROTATION_SAMPLES,
		help="rotation samples for each polar pixel [default=%default]")

	parser.add_option_group(transformation_option_group)

	return parser


parser = parse_options()
options,pargs = parser.parse_args()

if not len(pargs):
	parser.print_help()
	sys.exit()


#------------------------------------------------------


group = getattr(options,'group')
fourier_data_set = getattr(options,'fourier-data-set')
polar_data_set = getattr(options,'polar-data-set')

polar_rows = getattr(options,'polar-rows')
polar_cols = getattr(options,'polar-cols')
polar_radius = getattr(options,'polar-radius')
radius_samples = getattr(options,'radius-samples')
rotation_samples = getattr(options,'rotation-samples')


#------------------------------------------------------

# go through the hdf files that are input

for hfname in pargs:
	print('processing', hfname)

	if not os.path.isfile(hfname):
		print('Error locating', hfname)
		sys.exit()

	try: hfile = h5py.File(hfname)
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

	try: fourier_img = data_grp[fourier_data_set]
	except:
		err_fmt_str = 'Error finding dataset {} in HDF group {}'
		err_str = err_fmt_str.format(fourier_data_set, group)
		print(err_str)
		print('closing', hfname)
		hfile.close()
		print('Exiting', sys.argv[0])
		sys.exit()



	# get the power spectrum 
	power_img = numpy.abs(fourier_img)**2

	# centre the power spectrum
	power_img = cryoem.recentre_image(power_img)

	# get the polar image
	polar_img = cryoem.polar_ft(power_img, polar_rows, polar_cols,
				polar_radius, radius_samples, rotation_samples)


# --save the array for the polar image

	try:
		if polar_data_set in data_grp: del data_grp[polar_data_set]
	except:
		err_fmt = 'Error checking HDF group {} for {}'
		err_str = err_fmt.format(group,polar_data_set)
		print(err_str)

		print('closing', hfname)
		hfile.close()
		print('Exiting', sys.argv[0])
		sys.exit()

	try: dset = data_grp.create_dataset(polar_data_set,data=polar_img)

	except:
		err_fmt = "Error creating dataset '{}' in HDF group {}"
		err_str = err_fmt.format(polar_data_set,data_grp)
		print(err_str)

		print('closing', hfname)
		hfile.close()

		print('Exiting', sys.argv[0])
		sys.exit()

	dset.attrs['polar-rows'] =  polar_rows
	dset.attrs['polar-cols'] =  polar_cols
	dset.attrs['polar-radius'] =  polar_radius
	dset.attrs['radius-samples'] =  radius_samples
	dset.attrs['rotation-samples'] =  rotation_samples

	hfile.close()
