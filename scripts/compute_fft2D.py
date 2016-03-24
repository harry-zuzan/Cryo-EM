#!/usr/bin/env python2

# Adds a Fourier transform to a group with image data

from __future__ import print_function

import optparse, sys, os
import subprocess

import numpy, h5py

import platform

print('Python version', platform.python_version())


GROUP = 'Observed'
SPATIAL_DATA_SET = 'real image'
FOURIER_DATA_SET = 'fourier image'

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

	option_group.add_option("--fourier-data-set",
		dest='fourier-data-set', default=FOURIER_DATA_SET,
		help="Fourier transform data set name [default=%default]")

	parser.add_option_group(option_group)

	return parser


# ----------------------------------------------------------------------


parser = parse_options()
options,pargs = parser.parse_args()

if not len(pargs):
	parser.print_help()
	sys.exit()



group = getattr(options,'group')
spatial_data_set = getattr(options,'spatial-data-set')
fourier_data_set = getattr(options,'fourier-data-set')

# ----------------------------------------------------------------------


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
		err_str = 'Error finding dataset {} in HDF group {}'.format(spatial_data_set, group)
		print(err_str)
		print('closing', hfname)
		hfile.close()
		print('Exiting', sys.argv[0])
		sys.exit()

	real_data = real_dset[:].astype(numpy.float)
	fft_data = numpy.fft.fft2(real_data,norm="ortho")

	try:
		if fourier_data_set in data_grp: del data_grp[fourier_data_set]
	except:
		err_str = 'Error checking HDF group {} for {}'.format(group,fourier_data_set)
		print(err_str)
		print('closing', hfname)
		hfile.close()
		print('Exiting', sys.argv[0])
		sys.exit()

	try: data_grp.create_dataset(fourier_data_set,data=fft_data)
	except:
		err_str = 'Error dataset {} in HDF group {},norm="ortho"'.format(fourier_data_set,group)
		print(err_str)
		print('closing', hfname)
		hfile.close()
		print('Exiting', sys.argv[0])
		sys.exit()

	hfile.close()
