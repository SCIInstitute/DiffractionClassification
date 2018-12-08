import dm3_lib as dm3
import numpy as np

from matplotlib import pyplot as plt


def tif_extract(filepath):	

	# Read in the dat as a Numpy array
	image_data =  plt.imread(fpath)
	
	print(image_data.shape)

	# Due to the lack of a universal schema for metatags at the current time
	# we leave it to the user to proscribe the relevant calibrations	

	return image_data


def dm3_extract(filepath):
	"""
	DM3 data is assumed to be an image unless stated in the session
	"""

	# Read in the data as a numpy array
	dm3_file = dm3.DM3(filepath)
	
	image_data = dm3_file.imagedata

	print(image_data.shape)

	# Due to the lack of a universal schema for metatags at the current time
	# we leave it to the user to proscribe the relevant calibrations

	return image_data	

def csv_extract(filepath):
	"""
	Data is expected to be a profile in rows or columns with no headers.
	Singular profiles are expected to be in pixels unless a scale bar is explicitly supplied 
	"""

	csv_file = np.genfromtxt(open(filepath, "rb"), delimiter=",")
	image_data = csv_file

	# Orients columnar data into rows if necessary 
	print(image_data.shape)
	if len(image_data.shape) != 1:
		if image_data.shape[0] > image_data.shape[1]:
			image_data = image_data.T
			print(image_data.shape)
	
	# Due to the lack of a universal schema for metatags at the current time
	# we leave it to the user to proscribe the relevant calibrations

	return image_data

def txt_extract(filepath):


	# Read in the data as a numpy array

	text_file = np.genfromtxt(open(filepath, "rb"), delimiter="\t")
	image_data = text_file

	# Orients columnar data into rows if necessary 
	print(image_data.shape)
	if len(image_data.shape) != 1:
		if image_data.shape[0] > image_data.shape[1]:
			image_data = image_data.T
			print(image_data.shape)


	# Due to the lack of a universal schema for metatags at the current time
	# we leave it to the user to proscribe the relevant calibrations

	return image_data