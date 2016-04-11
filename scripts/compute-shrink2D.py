#!/usr/bin/env python2

# Computes wavelet shrinkage of the data

from __future__ import print_function

import optparse, sys, os
import subprocess

import numpy, h5py, pywt
from bws import bws2d

import platform

print('Python version', platform.python_version())


IMAGE_GROUP = 'Observed'
SHRUNK_GROUP = 'Shrunk'
IMAGE_DATA_SET = 'real image'
SHRUNK_DATA_SET = 'real image'
LIKELIHOOD_PREC = None
PRIOR_EDGE_PREC = 1.0
PRIOR_DIAG_PREC = -numpy.sqrt(0.5)
WAVELET= 'sym8'
TRACKS = [99]


def parse_options():
	usage = "usage: %prog [options] hdf-image-files"

	parser = optparse.OptionParser(usage=usage)

	# Internal to the parser
	file_option_group = optparse.OptionGroup(parser,"File Access",
		"Where to access input and store oputput in hdf data files")

	file_option_group.add_option("--image-group",
		dest='image-group', default=IMAGE_GROUP,
		help="input image group name [default=%default]")

	file_option_group.add_option("--shrunk-group",
		dest='shrunk-group', default=SHRUNK_GROUP,
		help="input image group name [default=%default]")

	file_option_group.add_option("--image-data-set",
		dest='image-data-set', default=IMAGE_DATA_SET,
		help="input image data set name [default=%default]")

	file_option_group.add_option("--shrunk-data-set",
		dest='shrunk-data-set', default=SHRUNK_DATA_SET,
		help="shrunk image data set name [default=%default]")

	parser.add_option_group(file_option_group)

	analysis_option_group = optparse.OptionGroup(parser,"Analysis Agruments",
		"Values of arguments passed to analysis methods")

	analysis_option_group.add_option("--wavelet", 
		dest="wavelet", default=WAVELET,
		choices=pywt.wavelist(),
		help="wavelet to use for shrinkage [default=%default]")


	analysis_option_group.add_option("--edge-prec",
		dest="edge-prec", type="string", default=PRIOR_EDGE_PREC,
		help='precision in prior of edge neighbours [default=%default]')

	analysis_option_group.add_option("--diagonal-prec",
		dest="diagonal-prec", type="string", default=PRIOR_DIAG_PREC,
		help='precision in prior of diagonal neighbours [default=%default]')

	def parse_lprec(option, opt_str, value, parser):
		lprec_tuple = eval(value)
		setattr(parser.values,option.dest,lprec_tuple)


	analysis_option_group.add_option("--likelihood-prec",
		action="callback", callback=parse_lprec,
		dest="likelihood-prec", type="string", default=LIKELIHOOD_PREC,
		help='precision of likelihood function [default=%default]')


	parser.add_option_group(analysis_option_group)

	return parser


# ----------------------------------------------------------------------


parser = parse_options()
options,pargs = parser.parse_args()

if not len(pargs):
	parser.print_help()
	sys.exit()


image_group = getattr(options,'image-group')
shrunk_group = getattr(options,'shrunk-group')
                        
image_data_set = getattr(options,'image-data-set')
shrunk_data_set = getattr(options,'shrunk-data-set')


wavelet = getattr(options,'wavelet')

eprec = getattr(options,'edge-prec')
dprec = getattr(options,'diagonal-prec')
lprec = getattr(options,'likelihood-prec')


# identify the precision relative to likelihood
prior_prec_sum = 4.0*(abs(eprec) + abs(dprec))
eprec_std = eprec/prior_prec_sum
dprec_std = dprec/prior_prec_sum


Wavelet = pywt.Wavelet(wavelet)


for hfname in pargs:
	print(hfname)
	hfile = h5py.File(hfname)
	arr2d = hfile[image_group][image_data_set][:].astype(numpy.float64)

	coeffs = pywt.wavedec2(arr2d,Wavelet)

	for k in range(len(lprec)):
		lprec_k = lprec[k]

		coeffs[-(k+1)][0][:] = bws2d(coeffs[-(k+1)][0],
								eprec_std, dprec_std, lprec[k])
		coeffs[-(k+1)][1][:] = bws2d(coeffs[-(k+1)][1],
								eprec_std, dprec_std, lprec[k])
		coeffs[-(k+1)][2][:] = bws2d(coeffs[-(k+1)][2],
								eprec_std, dprec_std, lprec[k])

	arr2d_shrunk = pywt.waverec2(coeffs,Wavelet)

	if not shrunk_group in hfile: hfile.create_group(shrunk_group)
	sgrp = hfile[shrunk_group]

	if shrunk_data_set in sgrp: del sgrp[shrunk_data_set]
	sdset = sgrp.create_dataset(shrunk_data_set, data=arr2d_shrunk)

	sdset.attrs['wavelet'] = wavelet
	sdset.attrs['likelihood precision'] = lprec
	sdset.attrs['prior edge precision'] = eprec
	sdset.attrs['prior diagonal precision'] = dprec

	hfile.close()

#	break
