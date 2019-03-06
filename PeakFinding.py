from __future__ import print_function
from __future__ import division

import numpy as np
from matplotlib import pyplot as plt

def vote_peaks(signal, filter_size=1,passes=2,threshold=.8):
    """
        Input: 

        signal : dictionary, contains two_theta, d_spacings, and input_vector arrays
                    peaks locations found in the profile 

        filter_size : int, starting bin width of each pass
        
        passes : int, number of voting rounds 
        
        thresh : 0 < float < 1, percentage votes to be considered a peak 
        
    Outputs:

        payload : dictionary, contains classification statistics and predictions
    
    """

	# determine size of filter
    size = len(signal)
    
    # Pad profile so it can be indexed properly   
    signal = np.pad(signal,(filter_size+passes,filter_size+passes),'constant', constant_values=(0))
    

    # create vote holder array
    votes = np.zeros_like(signal)
 
    # iterate over the array accruing votes for the tallest peaks
    for j in range(passes):

        # step through the array and vote for peak locations 
        for i in range(0,size+j):
            scalar = 1
            votes[np.argmax(signal[i:i+filter_size+j])+i] += scalar
        
        # Pare down the votes to remove extraneous peaks but preserve candidates
        votes[votes<np.amax(votes)*threshold] = 0        


    # trim off the padding from the votes array
    inner = (filter_size+passes)
    peak_locs_pixel = votes[inner:-inner]

    return peak_locs_pixel




def pixel2theta(x,SIZE=1e-9,DIST=300.0,WAVE=1.54046):
    """
    Inputs:
        x : array, vector of bins
        SIZE: float, pixel_size in microns/pixel
        DIST: float, distance of camera from sample in millimeters
        WAVE: float, wave length in nanometers
    Outputs:

        theta: array, vector of two theta values
        d: array, vector of d space values 

    """
        
    r = x*SIZE*1e-3 #in millimeters
    d = DIST * WAVE / r
    

    theta = np.arcsin((1/(d)))*360/np.pi #radians->degrees*2
    
    return theta, d

def profile2theta(pixel_profile,SIZE=1e9,WAVE=.15406):
    """
    Inputs:
        pixel_profile : array, vector of bins in inverse D
        SIZE: float, pixel_size in microns/pixel
        WAVE: float, wave length in nanometers
    Outputs:

        t_scale: array, vector of two theta values
        rd_scale: array, vector of d space values 

    """

    id_scale = np.linspace(0.00001,len(pixel_profile),len(pixel_profile))*SIZE
    
    rd_scale = 1/id_scale
    
    t_scale = d2theta(rd_scale,WAVE)
    
    return t_scale, rd_scale

def d2theta(d,wavelength=.15406):
    """
    Inputs:
        pixel_profile : array, vector of bins in D
        WAVE: float, wave length in nanometers
    Outputs:

        theta_vec: array, vector of two theta values
    """

    theta_vec = 2 * np.arcsin(wavelength/(d*2)) * 180/np.pi
    return theta_vec

def plot_peaks(signal,scale,votes,display_type):

    """
    Inputs:
        signal : array, vector of bins in inverse D
        scale: array, pixel_size in microns/pixel
        votes: array, wave length in nanometers
        display_type: string, d or theta

    Outputs:

        None
        
    """

    indicies = np.where(votes>0)
    plt.figure(figsize=(6,2))
    plt.plot(scale,signal,linewidth=3)
    sig_min = np.amin(signal)

    counter = 1
    for index in indicies[0]:
        x = np.array([scale[index],scale[index]])
        y = np.array([signal[index],sig_min])
        plt.plot(x,y,linewidth=2,label="peak {}".format(counter))
        counter += 1 
    
    if display_type == "d":
        plt.xlim(.5,6)
        plt.title("d spacing")
    elif display_type == "theta":
        plt.xlim(0,110)
        plt.title("two theta")
    

    plt.legend()
    plt.show(block=False)

