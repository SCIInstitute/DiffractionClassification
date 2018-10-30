import dm3_lib as dm3
import numpy as np

from matplotlib import pyplot as plt


"""
"""
def ensure_positivity(image):
	"""
	NOT YET IMPLEMENTEDs
	"""
	#minimum = np.amin(image)
	#image -= minimum
	pass
	
"""
"""
def tif_extract(filepath):	

	image_data =  plt.imread(fpath)
	
	ensure_positivity(image_data)
	
	
	# determine if the data is a profile or a diffraction pattern
	# NOT YET IMPLEMENTED
	print(image_data.shape)


	# Due to the lack of a universal schema for metatags at the current time
	# we leave it to the user	

	return image_data


"""
"""
def dm3_extract(filepath):

	dm3_file = dm3.DM3(filepath)
	#help(dm3_file)
	#print(dm3_file.__dict__)
	image_data = dm3_file.imagedata


	# determine if the data is a profile or a diffraction pattern
	# NOT YET IMPLEMENTED
	print(image_data.shape)

	#print help(image_data)
	
	# Due to the lack of a universal schema for metatags at the current time
	# we leave it to the user


	return image_data

"""
"""
def csv_extract(filepath):

	csv_file = np.genfromtxt(open(filepath, "rb"), delimiter=",")
	#help(dm3_file)
	#print(dm3_file.__dict__)
	image_data = csv_file

	# determine if the data is a profile or a diffraction pattern
	# NOT YET IMPLEMENTED
	print(image_data.shape)
	if len(image_data.shape) != 1:
		if image_data.shape[0] > image_data.shape[1]:
			image_data = image_data.T
			print(image_data.shape)
	#print help(image_data)
	
	# Due to the lack of a universal schema for metatags at the current time
	# we leave it to the user

	return image_data