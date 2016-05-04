import numpy
cimport numpy

# read the tutorial first
from libc.math cimport cos, sin
from libc.math cimport M_PI

# radial sampling of the wedge for each radial increment 
# a new one must be computed for each increment of the radius
# at this point computing these radii is not so expensive
def get_sampling_radii(rad1,rad2,nrad):
	# take the square root to sample mini-wedges of equal area
	root_rad1,root_rad2 = numpy.sqrt(rad1), numpy.sqrt(rad2)
	root_radii = numpy.linspace(root_rad1,root_rad2,nrad+1)
	radii = numpy.zeros((nrad,),numpy.double)

	for k in range(nrad): radii[k] = 0.5*(root_radii[k] + root_radii[k+1])

	return radii*radii


def get_sampling_angles(nrows,nrot):
	rbounds = numpy.linspace(0.0, 2.0*numpy.pi/nrows, nrot+1)
	rotns = [(0.5*(rbounds[k] + rbounds[k+1])) for k in range(nrot)]
	return numpy.array(rotns)


def polar_ft(numpy.ndarray[numpy.float64_t,ndim=2] power_img,
			int polar_rows, int polar_cols, double polar_radius,
			int radius_samples, int rotation_samples):

	cdef int N1 = power_img.shape[0]
	cdef int N2 = power_img.shape[1]

	cdef numpy.ndarray[numpy.float64_t,ndim=2] polar_img = \
        numpy.zeros((polar_rows,polar_cols), dtype=numpy.float64)

	cdef max_radius = polar_radius*0.5*min(N1,N2)

	cdef int i, j

	cdef numpy.ndarray[numpy.float64_t,ndim=1] radius_steps = \
		numpy.linspace(0.0,max_radius,polar_cols+1)

	cdef numpy.ndarray[numpy.float64_t,ndim=1] rotation_steps = \
		numpy.linspace(0.0,2.0*numpy.pi,polar_rows+1)

	cdef numpy.ndarray[numpy.float64_t,ndim=1] sampling_angles = \
		get_sampling_angles(polar_rows,rotation_samples)

	cdef double centre_x = power_img.shape[1]/2.0 + 0.5
	cdef double centre_y = power_img.shape[0]/2.0 + 0.5

	cdef double rad1, rad2
	cdef double rotn, radius
	cdef double x, y
	cdef int crow, ccol

	cdef double pixel_sum


	# Assuming cryo-em images with an even number of pixels - never seen odd
	# The centre of the fourier power spectrum is the pixel to the right
	# of y and below x

	# start in the middle going out
	for pcol from 0 < pcol < polar_cols:
		rad1,rad2 = radius_steps[pcol], radius_steps[pcol+1]
		radii = get_sampling_radii(rad1,rad2,radius_samples)

		# go around the circle in uniform steps as with radii but no square root
		for prow in range(polar_rows):
#			shift_rotn = 2.0*numpy.pi*numpy.float(prow)/numpy.float(polar_rows)
			shift_rotn = 2.0*M_PI*<double>(prow)/<double>(polar_rows)
			rotns = sampling_angles + shift_rotn

			# the sampling points of the cartesian image in polar coordinates
			# will be the cross product of radii and rotns

			# now sample the wedge
			pixel_sum = 0.0

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
			polar_img[polar_rows - prow - 1,pcol] = pixel_sum

	return polar_img
