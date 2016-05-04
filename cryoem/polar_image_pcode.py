
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



# rotational sampling of the wedge for the first rotational increment
# these can be incremented around the whole rotation by addition
# so only one needs to be created

def get_sampling_angles(nrows,nrot):
	rbounds = numpy.linspace(0.0, 2.0*numpy.pi/nrows, nrot+1)
	rotns = [(0.5*(rbounds[k] + rbounds[k+1])) for k in range(nrot)]
	return numpy.array(rotns)


#	# out to the max radius and around the pi
#	radius_steps = numpy.linspace(0.0,max_radius,polar_cols+1)
#	rotation_steps = numpy.linspace(0.0,2.0*numpy.pi,polar_rows+1)
#	rotation_image = numpy.zeros((polar_rows,polar_cols),numpy.double)
#
#	sampling_angles = get_sampling_angles(polar_rows,rotation_samples)
#
#	# Assuming cryo-em images with an even number of pixels - never seen odd
#	# The centre of the fourier power spectrum is the pixel to the right
#	# of y and below x
# 
#	centre_x = power_img.shape[1]/2.0 + 0.5
#	centre_y = power_img.shape[0]/2.0 + 0.5
#
#	# start in the middle going out
#	for pcol in range(polar_cols):
#
#		rad1,rad2 = radius_steps[pcol], radius_steps[pcol+1]
#		radii = get_sampling_radii(rad1,rad2,radius_samples)
#
#		# go around the circle in uniform steps as with radii but no square root
#		for prow in range(POLAR_ROWS):
#			shift_rotn = 2.0*numpy.pi*numpy.float(prow)/numpy.float(POLAR_ROWS)
#			rotns = sampling_angles + shift_rotn
#
#			# the sampling points of the cartesian image in polar coordinates
#			# will be the cross product of radii and rotns
#
#			# now sample the wedge
#			pixel_sum = 0.0
#
#			for radius in radii:
#				for rotn in rotns:
#					x = radius*numpy.cos(rotn)
#					y = radius*numpy.sin(rotn)
#					crow = numpy.int(centre_y - y)
#					ccol = numpy.int(centre_x + x)
#					pixel_sum += power_img[crow,ccol]
#
#			pixel_sum /= radius_samples*rotation_samples
#			rotation_image[polar_rows - prow - 1,pcol] = pixel_sum
#
