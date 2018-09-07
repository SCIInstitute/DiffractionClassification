from __future__ import print_function
from __future__ import division


import numpy as np


def find_center(image,beam_stop=False):
    """
    Find the center of the image

    Inputs:

        image 		: np.array, contains the diffraction data to analyze
        beam_stop	: boolean,  represents whether the beamstop is present in the image

    Outputs:

        x,y: integers,  the index coordinates of the central peak

    """

    if beam_stop:
        raise ValueError("Beam stop analysis not implemented yet.")		
    else:

        # We exclude the top n=3 pixels to avoid weird interactions on the detector
        ordered_points = np.dstack(np.unravel_index(np.argsort(image.ravel()), image.shape))[:,:-2]

        # Extract the nth pixel from the list ordered on intensity.
        center = ordered_points[:,-3][0]
        print(ordered_points[:,-10:][0])
        #print(center)


    return center

"""
"""
def radial_profile(data, center,bins=1):
    """
    Create the azimuthal integration from the data

    Inputs:

        data		: np.array,  contains the diffraction data to analyze
        center 		: tuple(x,y), the index coordinates of the central peak

    Outputs:

        radius			: np.array(1,N), range of pixel distance
        brightness 		: np.array(1,N), array of values for the integration

    """

    # Create the indicies array masked array

    y,x = np.indices((data.shape)) # first determine radii of all pixels
    
    # Modify the indicies to incorporate pixel distance
    r = np.sqrt((x-center[1])**2+(y-center[0])**2)    
    print("CENTER",center)#debug
    #print("AFDSKHADSF",r.shape)#debug
    # Radius of the image
    r_max = np.max(r)  

    # Evaluate the brightnesses of each ring in the indicies array
    ring_brightness, radius = np.histogram(r, weights=data, bins=int(r_max)//bins)
    
    #print(ring_brightness.shape)#debug
    return radius[1:], ring_brightness

