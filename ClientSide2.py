from __future__ import print_function
from __future__ import division

from Notation import SpaceGroupsDict as spgs

notation_dictionary = spgs.spacegroups()

import PeakFinding2 as pfnd #custom library to handle the functions behind Find_Peaks
import UniversalLoader2 as uvll #custom library to handle the functions behind UniversalLoader
import requests

import numpy as np

def Load_Profile(path,get_metadata=False):
    """
    Loads an image and extracts the relevant metadata for the image based in file type
    
    Inputs:

       path : string, contains the location of the file on the local machine

    Outputs:

       image_data   : np.array, the array of values in the image
       calibration  : dictionary, the essential metadata to convert from pixels to two_theta space

    """

    """
    NEEDS A BUNCH OF CONDITIONALS TO DETERMINE
    THE NATURE OF THE DATA, BEING IN SOOOOO MANY FORMS
    """
    valid_filetypes={".csv":uvll.csv_extract,
                    ".txt":uvll.txt_extract}
    
    file_type = path[-4:]

    # Check that the provided file is a supported file type
    if file_type in valid_filetypes.keys():
        
        # Call the appropriate extraction function
        profile,scale =  valid_filetypes[file_type](path)

    else:

        raise ValueError("Unsupported file type: please use a {}".format(valid_filetypes.keys()))

    return profile,scale

def Find_Peaks(profile,scale):
    """
    Pulls out the peaks from a radial profile


    Inputs:

        profile     : dictionary, contains intensity profile and pixel scale of
                                  diffraction pattern
        calibration : dictionary, contains camera parameters to scale data
                                 properly in two theta space
        is_profile  : boolean, changes processing for profiles vs 2D patterns 
        scale_bar   : string, determines which conversions need to be run  
                            to convert to two theta
        display_type: string, determines which plots to show


    Outputs:

        peak_locs : dictionary, contains two_theta, d_spacings, and input_vector arrays
                            peaks locations found in the profile
    
    """

    squished_scale = [True if x<6 and x >.5 else False for x in scale]

    filter_size=max(int(scale[squished_scale].shape[0]/50),3)
    
    # find the location of the peaks in pixel space    
    peaks = pfnd.vote_peaks(profile[squished_scale],filter_size=filter_size)
    
    peaks_d = scale[squished_scale][peaks>0]
    scale_d = scale
   
    peak_locs = {"d_spacing":scale[squished_scale][peaks>0],
                "vec":[int(round((x-.5)*164))-1 for x in peaks_d]
        }

    # Display the data
    pfnd.plot_peaks(profile[squished_scale],scale[squished_scale],peaks)

    if len(peak_locs['vec']) <= 2:
        print("WARNING: only {} peaks were detected," + 
            " this is lower than the recommended 4+ peaks needed"+
            "\nfor best results. Please check calibration.".format(len(peaks_d)))


    return peak_locs


def Send_For_Classification(peak_locations,user_info,URL,fam=None):
    """
    Input: 

        peak_locs : dictionary, contains two_theta, d_spacings, and input_vector arrays
                    peaks locations found in the profile 

        user_info : dictionary, contains user profile information for tracking 
                    and security purposes

    Outputs:

        payload : dictionary, contains classification statistics and predictions
    
    Calls:

        URL: POST, sends peak locations to the server for classification    

    """

    int_to_fam = {0:"triclinic",
                  1:"monoclinic",
                  2:"orthorhombic",
                  3:"tetragonal",
                  4:"trigonal",
                  5:"hexagonal",
                  6:"cubic"}


    payload = {'peaks':peak_locations['vec'],
                'level':"Family",
                'mode':"DiffOnly",
                'number':0
                }

    family = requests.post(URL+"predict", json=payload).json()
    
    payload['family'] = int_to_fam[np.argmax(family['votes'])]

    payload["level"] = "Genera"
    payload["number"] = int(np.argmax(family['votes']))+1
    
        
    # Once the family is known, predicts the genus
    genus = requests.post(URL+"predict", json=payload,timeout=30).json()
    
    genera_votes = np.sum(genus['votes'],axis=0).tolist()
    genera_pred = int(np.argmax(genera_votes)) + notation_dictionary.edges["genus"][payload['family']][0]


    # Configure payload json for next request
    payload["level"] = "Species"
    payload["number"] = genera_pred
    payload["genus"] = genera_pred
    
    # Once the genera are predicted give the top two from each
    species = requests.post(URL+"predict", json=payload,timeout=30).json()
    

    # Formatting the response to be saved more easily
    species_votes = int(np.argmax(species['votes']))
    species_pred = species_votes + notation_dictionary.edges["species"][genera_pred][0]
    
    # First prediction
    payload["species"] = species_pred

    
    return payload