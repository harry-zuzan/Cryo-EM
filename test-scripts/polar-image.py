import h5py, numpy
from PIL import Image

# the image to work on
hfname = 'test-polar/raw-stack00000.hdf5'
hfile = h5py.File(hfname,'r')
img = hfile['Shrunk']['fourier image'][:]
hfile.close()

# get the power
img = numpy.abs(img)**2
img[0,0] = img.min()

# centre the image
img = numpy.roll(img,img.shape[0]/2,0)
img = numpy.roll(img,img.shape[1]/2,1)

#img[:,:] = 0.0
#img[:,:144] = 1.0

# tall and skinny because the arc is longer than the radius
polar_rows = 128
polar_cols = 256

# go out this far to the edge given a unit radius
cartesian_radius = 0.35

# each rotation samples out and around
radius_samples = 8
rotation_samples = 8
max_radius = cartesian_radius*(min(*img.shape)/2)

print('max radius =', max_radius, 'pixels')

# out to the max radius and around the pi
radius_steps = numpy.linspace(0.0,max_radius,polar_cols+1)
rotation_steps = numpy.linspace(0.0,2.0*numpy.pi,polar_rows+1)

rotation_image = numpy.zeros((polar_rows,polar_cols),numpy.double)
# start in the middle going out
for pcol in range(polar_cols):
	# inside and outside edge of the wedge
	rad1,rad2 = radius_steps[pcol], radius_steps[pcol+1]
	print('pcol,rad1 =', pcol,rad1)
	
	# take the square root to sample mini-wedges of equal area
	root_rad1,root_rad2 = numpy.sqrt(rad1),numpy.sqrt(rad2)

	# radius of a mini-wedge in the square root world
	span = (root_rad2 - root_rad1)/radius_samples

	# step out half way into each mini wedge in the square root world
	root_radii = numpy.zeros((radius_samples,),numpy.double)
	for idx in range(radius_samples):
		root_radii[idx] = root_rad1 + idx*span + 0.5*span

	# these are the radii to step across
	radii = root_radii**2

	# go around the circle in uniform steps e as above but no square root
	for prow in range(polar_rows):
#		print('prow =', prow)
		rot1,rot2 = rotation_steps[prow], rotation_steps[prow+1]
		span = (rot2 - rot1)/rotation_samples

		rotns = numpy.zeros((rotation_samples,),numpy.double)

		for idx in range(rotation_samples):
			rotns[idx] = rot1 + idx*span + 0.5*span

		rotns += numpy.pi
	
		# now sample the wedge
		pixel_sum = 0.0

		for radius in radii:
			for rotn in rotns:
				x = radius*numpy.cos(rotn)
				y = radius*numpy.sin(rotn)
				crow = numpy.int(img.shape[0]/2 - y)
				ccol = numpy.int(x + img.shape[0]/2)
				pixel_sum += img[crow,ccol]

		pixel_sum /= radius_samples*rotation_samples
		rotation_image[prow,pcol] = pixel_sum

#		break

#	break

A = 255.0*img/img.max()
B = A.copy().astype(numpy.uint8)
I = Image.fromarray(B)
I.save('junk-raw.png')

pimg = rotation_image.copy()

A = 255.0*rotation_image/rotation_image.max()

B = A.copy().astype(numpy.uint8)
I = Image.fromarray(B)

I.save('junk-rot.png')

