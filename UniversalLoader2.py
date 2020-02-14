import dm3_lib as dm3
import numpy as np

from matplotlib import pyplot as plt


def tif_extract(filepath):	
	"""
	TIFs are assumed to be images unless stated in the session


	Inputs:

		filepath: string, location of data on drive

	Outputs:

		profile_data: array, 

	"""

	raise NotImplementedError

	# Due to the lack of a universal schema for metatags at the current time
	# we leave it to the user to proscribe the relevant calibrations	

	return image_data


def dm3_extract(filepath):
	"""
	DM3 data is assumed to be an image unless stated in the session


	Inputs:

		filepath: string, location of data on drive

	Outputs:

		image_data: array, 

	"""

	# Read in the data as a numpy array
	raise NotImplementedError
	# Due to the lack of a universal schema for metatags at the current time
	# we leave it to the user to proscribe the relevant calibrations

	return image_data	

def csv_extract(filepath):
	"""
	Data is expected to be a profile in rows or columns with no headers.
	Singular profiles are expected to be in pixels unless a scale bar is explicitly supplied 

	Inputs:

		filepath: string, location of data on drive

	Outputs:

		profile_data: array, 

	"""

	csv_file = np.genfromtxt(open(filepath, "r"), delimiter=",")
	profile_data = csv_file

	# Orients columnar data into rows if necessary 
	print(profile_data.shape)
	if len(profile_data.shape) != 1:
		if profile_data.shape[0] > profile_data.shape[1]:
			profile_data = profile_data.T
			print(profile_data.shape)
	
	# Due to the lack of a universal schema for metatags at the current time
	# we leave it to the user to proscribe the relevant calibrations

	return profile_data[1,:],profile_data[0,:]

def txt_extract(filepath):
	"""
	Data is expected to be a profile in rows or columns with no headers.
	Singular profiles are expected to be in pixels unless a scale bar is explicitly supplied 

	Inputs:

		filepath: string, location of data on drive

	Outputs:

		profile_data: array, 

	"""

	# Read in the data as a numpy array
	text_file = np.genfromtxt(open(filepath, "r"), delimiter="\t")
	profile_data = text_file

	# Orients columnar data into rows if necessary 
	print(profile_data.shape)
	if len(profile_data.shape) != 1:
		if profile_data.shape[0] > profile_data.shape[1]:
			profile_data = profile_data.T
			print(profile_data.shape)


	# Due to the lack of a universal schema for metatags at the current time
	# we leave it to the user to proscribe the relevant calibrations

	return profile_data
