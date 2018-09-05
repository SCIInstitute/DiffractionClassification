FindPeaks.py

def vote_peaks(signal, initial_filter_size=7,passes=3,threshold=.7):

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
        votes[votes<np.amax(votes)*thresh] = 0        


    # trim off the padding from the votes array
    inner = (filter_size+passes)
    
    peak_locs_pixel = votes[inner:-inner]

    return peak_locs_pixel


def pixel2theta(x,bin_scale,SIZE=PIXEL_SIZE,DIST=CAMERA_DIST,WAVE=WAVELENGTH):
    """
    Inputs:
        x : vector of bins
        bin_scale: pixels per bin
        SIZE: pixel_size in microns/pixel
        DIST: distance of camera from sample in millimeters
        WAVE: wave length in nanometers
    """
        
    r = x*bin_scale*SIZE*1e-3 #in millimeters
    d = DIST * WAVE / r
    

    theta = np.arcsin((1/(d)))*360/np.pi #radians->degrees*2
    
    return theta, d

def plot_peaks(profile, votes):
	"""
	Inputs:

		profile :
		votes 	:
	"""