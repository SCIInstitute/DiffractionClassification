from __future__ import print_function
from __future__ import division

import numpy as np
from matplotlib import pyplot as plt


def select_peaks(peaks,low=15,high=90):

    peaks[peaks<low] = -1
    peaks[peaks>high] = -1
    
    down_selected = peaks[peaks!=-1]


    return down_selected

def vote_peaks(signal, filter_size=1,passes=2,threshold=.8):
    
	#define how large of steps need to be taken
    size = len(signal)
    
    # Pad profile so that we can index properly   
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

    #return select_peaks(peak_locs_pixel)


def pixel2theta(x,SIZE=1e-9,DIST=1,WAVE=1):
    """
    Inputs:
        x : vector of bins
        bin_scale: pixels per bin
        SIZE: pixel_size in microns/pixel
        DIST: distance of camera from sample in millimeters
        WAVE: wave length in nanometers
    """
        
    r = x*SIZE*1e-3 #in millimeters
    d = DIST * WAVE / r
    

    theta = np.arcsin((1/(d)))*360/np.pi #radians->degrees*2
    
    return theta, d

def profile2theta(pixel_profile,SIZE=1e9,WAVE=.15406):
    id_scale = np.linspace(0.00001,len(pixel_profile),len(pixel_profile))*SIZE
    #print(id_scale)
    rd_scale = 1/id_scale
    #print(rd_scale)
    t_scale = d2theta(rd_scale,WAVE)
    #print(t_scale)
    return t_scale, rd_scale

def d2theta(d,wavelength=.15406):
    theta_vec = 2 * np.arcsin(wavelength/(d*2)) * 180/np.pi
    return theta_vec

def plot_peaks(sig,scale,votes,type):

    indicies = np.where(votes>0)
    plt.figure(figsize=(6,2))
    plt.plot(scale,sig,linewidth=3)
    sig_min = np.amin(sig)

    counter = 1
    for index in indicies[0]:
        x = np.array([scale[index],scale[index]])
        y = np.array([sig[index],sig_min])
        plt.plot(x,y,linewidth=2,label="peak {}".format(counter))
        counter += 1 
    if type == "d":
        plt.xlim(.5,6)
        plt.title("d spacing")
    elif type == "theta":
        plt.xlim(0,110)
        plt.title("two theta")


    plt.legend()
    plt.show(block=False)