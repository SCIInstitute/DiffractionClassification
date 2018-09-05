from __future__ import print_function
from __future__ import division

import numpy as np
import os

from matplotlib import pyplot as plt

"""
Find the center(brightest point) in an image
"""
def find_center(chunk):


	center = np.argmax(chunk)
	x = int(center%chunk.shape[0])
	y = int(center/chunk.shape[0])

	return (x,y)


"""
Create the radial profile from an image and a center
"""
def rad_prof(data, binscale=None):

	# find the indicies from the brightest spot
	center = find_center(data)
	print(center)
	y,x = np.indices((data.shape)) # first determine radii of all pixels

	# determine the radius of the image
	r = np.sqrt((x-center[0])**2+(y-center[1])**2)    

	# radius of the image.
	r_max = np.max(r)  

	# check if the user assigned a bin value
	if binscale:
		# assign bins based on binscale
		ring_brightness, radius = np.histogram(r, weights=data, bins=int(r_max//binscale))
	else:
		# assign bins without a binscale
		ring_brightness, radius = np.histogram(r, weights=data, bins=int(r_max))

	# returns the spaces of the radius and profile of the brightness
	return radius[1:], ring_brightness



"""
fit an exponential curve to a processed 1D signal 

#This is not applicable anymore since we changed our radial profiler

"""
def fit_exponential(processed_signal1d):

    # two term exponential
    def func(x,a,b,c,d):
        x=np.array(x)
        return (a * np.exp(-1*(b*x)) + c* np.exp(-1*(d*x)))
    
    # elucidate x,y
    x = processed_signal1d[0][:-10]
    y = processed_signal1d[1][:-10]

    # fit a curve to the signal
    initial_point = (1.0,1.0,1.0,1.0)
    #try:
    popt, pcov = curve_fit(func,x,y,p0=initial_point)

    # elucidate variables
    v1,v2,v3,v4 = popt[0],popt[1],popt[2],popt[3]
    
    # find residual
    residuals = y - np.array(func(x,float(v1),float(v2),float(v3),float(v4)))
    
    min_residual = np.amin(residuals)
    if min_residual < 0:
        residuals -= min_residual
        residuals += 1
    elif min_residual == 0:
        residuals += 1 
    else:
        residuals += 1

    
    return (x,residuals)

"""
Divide the image into sub portions 
"""
def make_chunks(image,divisions_x=4,divisions_y=4):
    chunks = []
    shape = image.shape
    x_div = shape[0]//divisions_x
    y_div = shape[1]//divisions_y
    for x in range(divisions_x):
        for y in range(divisions_y):
            #checking = np.zeros_like(image)
            #checking[x_div*x:x_div*(x+1),y_div*y:y_div*(y+1)] = 100#image[x_div*x:x_div*(x+1),y_div*y:y_div*(y+1)]
            #chunks.append(checking)
            chunks.append(image[x_div*x:x_div*(x+1),y_div*y:y_div*(y+1)])
    return chunks

"""
Save chunked images
"""
def save_images(chunks,signals1d,name,folder=os.getcwd()):
    """ Save the images sequentially """

    for i in range(len(chunks)):
        # set the path to save the images
        fname = os.path.join(folder,name +str(i)+ ".png")

        
        # save the image
        im = Image.fromarray(chunks[i])
        im.save(fname)
        
    # save the list of 1D signals as a pickle
    sig_name = os.path.join(folder,name + "_integrated" + ".pkl")
    with open(sig_name,'wb') as f:
        pickle.dump(signals1d,f)


"""
find the peaks in a signal
"""
def peak_finder(signal,filter_size=3,passes=5,thresh=.8):
    """
    Inputs:
    	signal: 1D array of floats
    	filters_size: int, how large of a window to start with
    	passes: int, how many passes of votes at increasing filter size
    """

    size = len(signal)
    possible=0
    
    #signal = np.pad(signal,(filter_size+passes*2,filter_size+passes*2),'constant', constant_values=(0))
    signal = np.pad(signal,(filter_size+passes,filter_size+passes),'constant', constant_values=(0))
    
    votes = np.zeros_like(signal)
    for j in range(passes):
        for i in range(0,size+j):
            scalar = 1
            votes[np.argmax(signal[i:i+filter_size+j])+i] += scalar
        
        votes[votes<np.amax(votes)*thresh] = 0        
        possible += filter_size+2*j

   #votes[votes<filter_size] = 0
    inner = (filter_size+passes)
    return votes[inner:-inner]

"""
plots the peaks on top of the signal
"""
def plot_peaks(sig,thetas,votes,name):
    indicies = np.where(votes>0)
    plt.figure(figsize=(6,2))
    
    plt.plot(thetas,sig,linewidth=3)
    sig_min = np.amin(sig)
    for index in indicies[0]:
        x = np.array([thetas[index],thetas[index]])
        y = np.array([sig[index],sig_min])
        plt.plot(x,y,linewidth=2)
        
    
    plt.savefig(name+".png", bbox_inches='tight')
    plt.show()

"""
Extracts necessary statistics from a dm3 or tiff file
"""
def extract_camera_settings(metadata):

	"""
	currently assumes the metadata is structured in a specific format
	associated with dm3/h5?
	"""

	camera_dist = metadata["ImageList"]["TagGroup0"]["ImageTags"]["Microscope Info"]["Actual Magnification"]
 	pixel_size = metadata["ImageList"]["TagGroup0"]["ImageData"]["Calibrations"]["Dimension"]["TagGroup0"]["Scale"]
 	#pixel_size = metadata["ImageList"]["TagGroup0"]["ImageTags"]["Acquisition"]["Device"]["CCD"]["PIXEL Size(um)"]
 	beam_kv =  metadata["ImageList"]["TagGroup0"]["ImageTags"]["Microscope Info"]["Voltage"]
 	 
	
	#return camera_dist, 1/pixel_size, beam_kv*1e-3
	return camera_dist, 1e3*pixel_size, beam_kv*1e-3

"""
Converts peaks to peak signal
"""
def votes_to_signal(votes,bins=180):

	pass