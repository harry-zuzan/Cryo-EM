#!/usr/bin/env python2

# Computes wavelet shrinkage of the data with resistance to
# outliers using a redescending likelihood method

from __future__ import print_function

import optparse, sys, os
import subprocess

import numpy, h5py, pywt
from bws import bws2d_redescend

import platform

print('Python version', platform.python_version())


IMAGE_GROUP = 'Observed'
SHRUNK_GROUP = 'Shrunk'
IMAGE_DATA_SET = 'real image'
SHRUNK_DATA_SET = 'real image'
LIKELIHOOD_PREC = None
PRIOR_EDGE_PREC = 1.0
PRIOR_DIAG_PREC = -numpy.sqrt(0.5)
REDESCEND_CVAL = 500.0
WAVELET= 'sym8'

REDESCEND_MAXITER=128


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

	shrinkage_option_group = optparse.OptionGroup(parser,"Shrinkage Agruments",
		"Values of arguments passed to Bayesian wavelet shrinkage methods")

	shrinkage_option_group.add_option("--wavelet", 
		dest="wavelet", default=WAVELET,
		choices=pywt.wavelist(),
		help="wavelet to use for shrinkage [default=%default]")


	shrinkage_option_group.add_option("--edge-prec",
		dest="edge-prec", type="string", default=PRIOR_EDGE_PREC,
		help='precision in prior of edge neighbours [default=%default]')

	shrinkage_option_group.add_option("--diagonal-prec",
		dest="diagonal-prec", type="string", default=PRIOR_DIAG_PREC,
		help='precision in prior of diagonal neighbours [default=%default]')

	def parse_lprec(option, opt_str, value, parser):
		lprec_tuple = eval(value)
		setattr(parser.values,option.dest,lprec_tuple)


	shrinkage_option_group.add_option("--likelihood-prec",
		action="callback", callback=parse_lprec,
		dest="likelihood-prec", type="string", default=LIKELIHOOD_PREC,
		help='precision of likelihood function [default=%default]')

	parser.add_option_group(shrinkage_option_group)


	residual_option_group = optparse.OptionGroup(parser,
		"Outlier handling arguments",
		"Values of arguments passed to outlier influence reduction methods")

	residual_option_group.add_option("--redescend-cval",
		dest="redescend-cval", type="float", default=REDESCEND_CVAL,
		help="large standard deviation for redescending likelihood [default=%default]")

	residual_option_group.add_option("--redescend-maxiter",
		dest="redescend-maxiter", type="int", default=REDESCEND_MAXITER,
		help='max iterations for redescending likelihood [default=%default]')

	parser.add_option_group(residual_option_group)

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
lprec = numpy.array(lprec).astype(numpy.double)

cval = getattr(options,'redescend-cval')
maxiter = getattr(options,'redescend-maxiter')


# identify the precision relative to likelihood
prior_prec_sum = 4.0*(abs(eprec) + abs(dprec))
eprec_std = eprec/prior_prec_sum
dprec_std = dprec/prior_prec_sum


Wavelet = pywt.Wavelet(wavelet)


for hfname in pargs:
	print(hfname)
	hfile = h5py.File(hfname)
	arr2d = hfile[image_group][image_data_set][:].astype(numpy.float64)

	arr2d_shrunk,niter = bws2d_redescend(arr2d, eprec, dprec, lprec,
				wavelet, cval, maxiter)

	if not shrunk_group in hfile: hfile.create_group(shrunk_group)
	sgrp = hfile[shrunk_group]

	if shrunk_data_set in sgrp: del sgrp[shrunk_data_set]
	sdset = sgrp.create_dataset(shrunk_data_set, data=arr2d_shrunk)

	sdset.attrs['wavelet'] = wavelet
	sdset.attrs['likelihood precision'] = lprec
	sdset.attrs['prior edge precision'] = eprec
	sdset.attrs['prior diagonal precision'] = dprec
	sdset.attrs['redescend cval'] = cval
	sdset.attrs['redescend iterations'] = niter
	sdset.attrs['redescend maximum iterations'] = maxiter

	hfile.close()

#	break
