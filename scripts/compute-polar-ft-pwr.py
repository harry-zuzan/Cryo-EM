#!/usr/bin/env python2

# Writes the power spectrum in polar coordinates

from __future__ import print_function

import optparse, sys, os
import subprocess

import numpy, h5py

import platform
print('Python version', platform.python_version())


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

 
# the Fourier transform needs to be recentred to visualise the symmetry
def recentre_image(the_img):
	the_img = numpy.roll(the_img,the_img.shape[0]/2,0)
	the_img = numpy.roll(the_img,the_img.shape[1]/2,1)
	return the_img

# radial sampling of the wedge for each radial increment 
# a new one must be computed for each increment of the radius
def get_sampling_radii(rad1,rad2,nrad):
	# take the square root to sample mini-wedges of equal area
	root_rad1,root_rad2 = numpy.sqrt(rad1),numpy.sqrt(rad2)
	root_radii = numpy.linspace(root_rad1,root_rad2,nrad+1)
	radii = numpy.zeros((nrad,),numpy.double)

	for k in range(nrad): radii[k] = 0.5*(root_radii[k] + root_radii[k+1])

	return radii*radii

# rotational sampleing of the wedge for the first rotational increment
# these can be incremented around the whole rotation by addition
# so only one needs to be created
def get_sampling_angles(nrows,nrot):
	rbounds = numpy.linspace(0.0, 2.0*numpy.pi/nrows, nrot+1)
	rotns = [(0.5*(rbounds[k] + rbounds[k+1])) for k in range(nrot)]
	return numpy.array(rotns)


# now go through the hdf files that are input

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
	power_img = recentre_image(power_img)

	max_radius = polar_radius*(min(*power_img.shape)/2)

	# out to the max radius and around the pi
	radius_steps = numpy.linspace(0.0,max_radius,polar_cols+1)
	rotation_steps = numpy.linspace(0.0,2.0*numpy.pi,polar_rows+1)
	rotation_image = numpy.zeros((polar_rows,polar_cols),numpy.double)

	sampling_angles = get_sampling_angles(polar_rows,rotation_samples)

	# Assuming cryo-em images with an even number of pixels - never seen odd
	# The centre of the fourier power spectrum is the pixel to the right
	# of y and below x
 
	centre_x = power_img.shape[1]/2.0 + 0.5
	centre_y = power_img.shape[0]/2.0 + 0.5

	# start in the middle going out
	for pcol in range(polar_cols):

		rad1,rad2 = radius_steps[pcol], radius_steps[pcol+1]
		radii = get_sampling_radii(rad1,rad2,radius_samples)

		# go around the circle in uniform steps as with radii but no square root
		for prow in range(POLAR_ROWS):
			shift_rotn = 2.0*numpy.pi*numpy.float(prow)/numpy.float(POLAR_ROWS)
			rotns = sampling_angles + shift_rotn

			# the sampling points of the cartesian image in polar coordinates
			# will be the cross product of radii and rotns

			# now sample the wedge
			pixel_sum = 0.0

			for radius in radii:
				for rotn in rotns:
					x = radius*numpy.cos(rotn)
					y = radius*numpy.sin(rotn)
					crow = numpy.int(centre_y - y)
					ccol = numpy.int(centre_x + x)
					pixel_sum += power_img[crow,ccol]

			pixel_sum /= radius_samples*rotation_samples
			rotation_image[polar_rows - prow - 1,pcol] = pixel_sum


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

	try: data_grp.create_dataset(polar_data_set,data=rotation_image)
	except:
		err_fmt = 'Error creating dataset {} in HDF group {}'
		err_str = err_fmt.format(polar_data_set,data_grp)
		print(err_str)

		print('closing', hfname)
		hfile.close()

		print('Exiting', sys.argv[0])
		sys.exit()

	hfile.close()
