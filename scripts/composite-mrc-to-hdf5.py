#!/usr/bin/env python2

from __future__ import print_function

import optparse, sys, os
import subprocess

import numpy, struct, h5py

import platform

print('Python version', platform.python_version())


HEADER_LEN = 1024

HDF5_PATH = 'data-hdf5'
GROUP = 'Observed'
DATA_SET = 'real image'

DIGITS=0
ROOT_NAME='image'

def parse_options():
	usage = "usage: %prog [options] mrc-file"

	parser = optparse.OptionParser(usage=usage)

	# Internal to the parser
	option_group = optparse.OptionGroup(parser,"Options",
		"Command line options")

	option_group.add_option("--hdf5-path",
		dest='hdf5-path', default=HDF5_PATH,
		help="path to hdf5 mrc file output [default=%default]")

	option_group.add_option("--root-name",
		dest='root-name', default=ROOT_NAME,
		help="root name for all hdf5 mrc files [default=%default]")

	option_group.add_option("--digits",
		dest='digits', default=DIGITS,
		help="number of digits in hdf5 mrc files [default=%default]")

	option_group.add_option("--group",
		dest='group', default=GROUP,
		help="image group name [default=%default]")

	option_group.add_option("--data-set",
		dest='data-set', default=DATA_SET,
		help="image data set name [default=%default]")

	parser.add_option_group(option_group)

	return parser

# ----------------------------------------------------------------------

parser = parse_options()
options,pargs = parser.parse_args()

if not len(pargs)==1:
	parser.print_help()
	sys.exit()


hdf5_path = getattr(options,'hdf5-path')
if hdf5_path[-1] == '/': hdf5_path = hdf5_path[:-1]

if not os.path.exists(hdf5_path):
	status = subprocess.call(['mkdir',hdf5_path])
	if status:
		print('error creating directory', hdf5_path)
		sys.exit()


root_name = getattr(options,'root-name')
digits = int(getattr(options,'digits'))
group = getattr(options,'group')
data_set = getattr(options,'data-set')

# ----------------------------------------------------------------------


fname = pargs[0]
print('Parsing images from', fname)


infile = open(fname,'r')
header = infile.read(HEADER_LEN)
ncol,nrow,nimg,mode = struct.unpack('<' + 4*'i',header[:16])

npix = ncol*nrow


fname_fmt = '{0}{1:d}{2}'.format('{0}/{1}{2:0>',digits,'d}.hdf5')

for k in range(nimg):
	infile.seek(HEADER_LEN + k*npix)
	byte_img = infile.read(npix*4)
	arr_img = numpy.fromstring(byte_img,numpy.float32).astype(numpy.double)

	arr_img.shape = nrow,ncol

	hfname = fname_fmt.format(hdf5_path,root_name,k)
	print(hfname)

	hfile = h5py.File(hfname)
	if not group in hfile: hfile.create_group(group)
	grp = hfile[group]
	hfile.attrs['observed data group'] = group

	if data_set in grp: del grp[data_set]
	grp.create_dataset(data_set,data=arr_img)
	grp.attrs['observed data'] = data_set

	hfile.close()

infile.close()
