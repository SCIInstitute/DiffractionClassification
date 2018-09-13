import dm3_lib as dm3
from matplotlib import pyplot as plt

import numpy as np

"""
"""
def ensure_positivity(image):

	minimum = np.amin(image)
	
		
	#image -= minimum

	
"""
"""
def tif_extract(filepath):	

	image_data =  plt.imread(fpath)
	
	ensure_positivity(image_data)
	
	# Due to the lack of a universal schema for metatags at the current time
	# we leave it to the user
	calibration = None

	return image_data, calibration


"""
"""
def dm3_extract(filepath):

	image_data = dm3.DM3(filepath).imagedata
	ensure_positivity(image_data)

	#print help(image_data)
	
	# Due to the lack of a universal schema for metatags at the current time
	# we leave it to the user
	calibration = None

	return image_data, calibration
