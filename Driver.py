from __future__ import print_function
from __future__ import division

import ClientSide #custom package

import hyperspy.api as hs
import os


# TESTING IMPORTS
import numpy as np
from matplotlib import pyplot as plt


TEST_PATH = os.path.join("/media/matt/18A7DD7079E938D2","Unknown Zone Patterns","04g_Fe Rich zaaa","04g_Fe Rich_zaaa.dm3")



if __name__ == "__main__":

	fpath = TEST_PATH

	#THIS WORKS FOR DM3 BUT NOT TIFF
	# load the data
	f = hs.load(fpath)

	# pull out the image
	image = f.data.copy()
	

	# this stuff is in dm3 but not in TIFF

	# pull out the metadata
	meta_data_dict = f.original_metadata
	
	# find the relevant meta_data
	#camera_dist, pixel_size, beam_kv = Processing.extract_camera_settings(meta_data_dict)
	#wavelength = PixelConversions.Kv2WaveLength(beam_kv)*1e9
	#pixel_size = 14
	#print(camera_dist,pixel_size,wavelength)
	
	pixel_size = 14.0213 #microns/pixel
	camera_dist = 373.1215 #millimeters
	wavelength = .02507921 #shrug

	calibration = {"pixel_size":pixel_size,
					"camera_distance":camera_dist,
					"wavelength":wavelength}

	#wavelength = .0025
	
	# create the radial profile of the data
	radial_profile = ClientSide.Extract_Profile(image)
	print(radial_profile["brightness"].shape)
	plt.plot(radial_profile['brightness'])
	plt.show()




	#print(radial_profile[0])
	peak_locs = ClientSide.Find_Peaks(radial_profile,calibration)

	print(peak_locs)