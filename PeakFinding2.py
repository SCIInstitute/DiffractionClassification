from __future__ import print_function
from __future__ import division

import numpy as np
from matplotlib import pyplot as plt

def vote_peaks(signal, filter_size=10,passes=2,threshold=.6):
    """
        Input: 

        signal : list, contains d_spacings in the profile 

        filter_size : int, starting bin width of each pass
        
        passes : int, number of voting rounds 
        
        thresh : 0 < float < 1, percentage votes to be considered a peak 
        
    Outputs:

        payload : dictionary, contains classification statistics and predictions
    
    """

	# determine size of filter
    size = len(signal)
    
    # Pad profile so it can be indexed properly   
    signal = np.pad(signal,(filter_size,filter_size),'constant', constant_values=(0))
    print(size,signal.shape)

    # create vote holder array
    votes = np.zeros_like(signal)
    scalar = 1

    # step through the array and vote for peak locations 
    for i in range(0,size):
        
        #print(np.argmax(signal[i:i+filter_size])+i)
        votes[np.argmax(signal[i:i+filter_size])+i] += scalar
  
    # Pare down the votes to remove extraneous peaks but preserve candidates
    votes[votes<np.amax(votes)*threshold] = 0        



    # trim off the padding from the votes array
    inner = filter_size
    peak_locs_pixel = votes[inner:-inner]

    return peak_locs_pixel




def plot_peaks(signal,scale,votes):

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
    plt.ion()
    plt.plot(scale,signal,linewidth=3)
    
    sig_min = np.amin(signal)

    counter = 1
    for index in indicies[0]:
        x = np.array([scale[index],scale[index]])
        y = np.array([signal[index],sig_min])
        plt.plot(x,y,linewidth=2,label="peak {}".format(counter))
        counter += 1 
    

    plt.xlim(.5,6)
    plt.xlabel("d spacing")
    plt.ylabel("intensity")
    

    plt.legend()
    plt.show()
    
    

