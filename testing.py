from future.builtins.misc import input

pixel_size = None
wavelength = None
camera_dist = None
counter = 0

while pixel_size == None:

	temp_size = input("Please enter a pixel size(assumed to be in angstroms) e.g. 14.1\n")
	try:
		float(temp_size)

		if temp_size > 0:
			pixel_size = temp_size
		else:
			print("please enter a valid pixel_size")
	except:
		print("please enter a valid pixel_size")


print(pixel_size)

    