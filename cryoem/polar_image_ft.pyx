import numpy
cimport numpy

# read the tutorial first
from libc.math cimport cos, sin, sqrt
from libc.math cimport M_PI


# The Fourier transform with image sum at (0,0) needs to be recentred
def recentre_image(the_img):
	the_img = numpy.roll(the_img,the_img.shape[0]/2,0)
	the_img = numpy.roll(the_img,the_img.shape[1]/2,1)
	return the_img


# radial sampling of the wedge for each radial increment 
# take the square root to sample mini-wedges of equal area
def get_sample_radii(double rad1, double rad2, int nrad):

	cdef numpy.ndarray[numpy.float64_t,ndim=1] root_radii = \
		numpy.linspace(sqrt(rad1),sqrt(rad2),nrad+1)

	cdef numpy.ndarray[numpy.float64_t,ndim=1] radii = \
		numpy.zeros((nrad,),numpy.double)

	for k from 0 < k < nrad:
		radii[k] = 0.5*(root_radii[k] + root_radii[k+1])

	return radii*radii


# angles from which to sample
# these can be added to as the arc of wedges is traversed
def get_sample_rotations(npolar_rows,nsamples):
	cdef numpy.ndarray[numpy.float64_t,ndim=1] rotations = \
		numpy.zeros((nsamples,), dtype=numpy.float64)

	cdef numpy.ndarray[numpy.float64_t,ndim=1] rotation_bounds = \
		numpy.linspace(0.0, 2.0*M_PI/npolar_rows, nsamples+1)

	for k from 0 < k < nsamples:
		rotations[k] = 0.5*(rotation_bounds[k] + rotation_bounds[k+1])

	return numpy.array(rotations)


def polar_ft(numpy.ndarray[numpy.float64_t,ndim=2] power_img,
		int npolar_rows, int npolar_cols, double polar_radius,
		int radius_samples, int rotation_samples):

	# the image that gets returned
	cdef numpy.ndarray[numpy.float64_t,ndim=2] polar_img = \
        numpy.zeros((npolar_rows,npolar_cols), dtype=numpy.float64)

	# how far out in the high frequency part of the power spectrum 
	cdef max_radius = \
		0.5*polar_radius*min(power_img.shape[0],power_img.shape[1])

	# bounds that correspond to each column of the polar image
	cdef numpy.ndarray[numpy.float64_t,ndim=1] radius_steps = \
		numpy.linspace(0.0,max_radius,npolar_cols+1)

	# bounds that correspond to each row of the polar image
	cdef numpy.ndarray[numpy.float64_t,ndim=1] rotation_steps = \
		numpy.linspace(0.0,2.0*M_PI,npolar_rows+1)

	# the coordinate of the centre of the power spectrum 
	cdef double centre_x = power_img.shape[1]/2.0 + 0.5   # column
	cdef double centre_y = power_img.shape[0]/2.0 + 0.5   # row

	# declare the array for sampling across the radius
	sample_radii = numpy.zeros((radius_samples,), dtype=numpy.float64)

	# sampling angles for rotation angle of zero
	# each row just adds another 2pi/npolar_rows to this vector
	cdef numpy.ndarray[numpy.float64_t,ndim=1] sample_rotations = \
		get_sample_rotations(npolar_rows,rotation_samples)


#herehere
	cdef int i, j

	cdef double rad1, rad2
	cdef double rotn, radius
	cdef double x, y
	cdef int crow, ccol

	cdef double pixel_sum


	# Assuming cryo-em images with an even number of pixels - never seen odd
	# The centre of the fourier power spectrum is the pixel to the right
	# of y and below x

	# start in the middle going out
	for pcol from 0 < pcol < npolar_cols:
		rad1,rad2 = radius_steps[pcol], radius_steps[pcol+1]
		sample_radii = get_sample_radii(rad1,rad2,radius_samples)

		# go around the circle in uniform steps as with radii but no square root
		for prow in range(npolar_rows):
			shift_rotn = 2.0*M_PI*<double>(prow)/<double>(npolar_rows)
			rotns = sample_rotations + shift_rotn

			# the sampling points of the cartesian image in polar coordinates
			# will be the cross product of radii and rotns

			# now sample the wedge
			pixel_sum = 0.0

			# really need to fix this up the radii are off
			for radius from 0 < radius < radius_samples:
				for k from 0 < k < rotation_samples:
					rotn = rotns[k]
#				for rotn in rotns:
					x = radius*cos(rotn)
					y = radius*sin(rotn)
					crow = numpy.int(centre_y - y)
					ccol = numpy.int(centre_x + x)
					pixel_sum += power_img[crow,ccol]

			pixel_sum /= radius_samples*rotation_samples
			polar_img[npolar_rows - prow - 1,pcol] = pixel_sum

	return polar_img
