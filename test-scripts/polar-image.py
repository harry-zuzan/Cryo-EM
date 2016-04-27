import h5py, numpy
from PIL import Image

# some definitions to get things going to a proper script

# tall and skinny because the arc is longer than the radius
POLAR_ROWS = 256
POLAR_COLS = 128

# go out this far to the edge given a unit radius
MAX_POLAR_RADIUS = 0.85

# each rotation samples out and around
RADIUS_SAMPLES = 8
ROTATION_SAMPLES = 8




# the image to work on
hfname = 'test-polar/raw-stack00000.hdf5'
hfile = h5py.File(hfname,'r')
img = hfile['Shrunk']['fourier image'][:]
hfile.close()

# get the power
img = numpy.abs(img)**2
img[0,0] = img.min()

# in case the image needs to be recentered.
# for the Fourier transform the centering will be off by half a row
def recentre_image(the_img):
	the_img = numpy.roll(the_img,the_img.shape[0]/2,0)
	the_img = numpy.roll(the_img,the_img.shape[1]/2,1)
	return the_img

def get_sub_radii(rad1,rad2,nrad):
	# take the square root to sample mini-wedges of equal area
	root_rad1,root_rad2 = numpy.sqrt(rad1),numpy.sqrt(rad2)
	root_radii = numpy.linspace(root_rad1,root_rad2,nrad+1)
	radii = numpy.zeros((nrad,),numpy.double)

	for k in range(nrad): radii[k] = 0.5*(root_radii[k] + root_radii[k+1])

	return radii*radii

def get_sampling_angles(nrows,nrot):
	rbounds = numpy.linspace(0.0, 2.0*numpy.pi/nrows, nrot+1)
	rotns = [(0.5*(rbounds[k] + rbounds[k+1])) for k in range(nrot)]
	return numpy.array(rotns)


img = recentre_image(img)

max_radius = MAX_POLAR_RADIUS*(min(*img.shape)/2)

print('max radius =', max_radius, 'pixels')

# out to the max radius and around the pi
radius_steps = numpy.linspace(0.0,max_radius,POLAR_COLS+1)
rotation_steps = numpy.linspace(0.0,2.0*numpy.pi,POLAR_ROWS+1)

rotation_image = numpy.zeros((POLAR_ROWS,POLAR_COLS),numpy.double)

sampling_angles = get_sampling_angles(POLAR_ROWS,POLAR_COLS)

centre_x = img.shape[1]/2.0
centre_y = img.shape[0]/2.0

# start in the middle going out
for pcol in range(POLAR_COLS):
	print('pcol =', pcol)

	rad1,rad2 = radius_steps[pcol], radius_steps[pcol+1]
	radii = get_sub_radii(rad1,rad2,RADIUS_SAMPLES)

	# go around the circle in uniform steps as with radii but no square root
	for prow in range(POLAR_ROWS):
		shift = 2.0*numpy.pi*numpy.float(prow)/numpy.float(POLAR_ROWS)
		rotns = sampling_angles + shift

		# now sample the wedge
		pixel_sum = 0.0

		for radius in radii:
			for rotn in rotns:
				x = radius*numpy.cos(rotn)
				y = radius*numpy.sin(rotn)
				crow = numpy.int(centre_x - y)
				ccol = numpy.int(centre_y + x)
				pixel_sum += img[crow,ccol]

		pixel_sum /= RADIUS_SAMPLES*ROTATION_SAMPLES
		rotation_image[POLAR_ROWS - prow - 1,pcol] = pixel_sum

#		break
#	break

A = 255.0*img/img.max()
B = A.copy().astype(numpy.uint8)
I = Image.fromarray(B)
I.save('junk-raw.png')

A = 255.0*rotation_image/rotation_image.max()

B = A.copy().astype(numpy.uint8)
I = Image.fromarray(B)

I.save('junk-rot.png')

