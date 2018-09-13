from __future__ import print_function
from __future__ import division


import ProfileExtraction as pfex #custom library to handle the functions behind Extract_Profile
import PeakFinding as pfnd #custom library to handle the functions behind Find_Peaks
import UniversalLoader as uvll #custom library to handle the functions behind UniversalLoader
import requests

"""
"""
def Load_Image(path,get_metadata=False):
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
    valid_filetypes={".tif":uvll.tif_extract,
                    ".dm3":uvll.dm3_extract,
                    }
    
    file_type = path[-4:]

    # Check that the provided file is a supported file type
    if file_type in valid_filetypes.keys():
        
        # Call the appropriate extraction function
        image_data, calibration  =  valid_filetypes[file_type](path)

    else:

        raise ValueError("Unsupported file type: please submit a {}".format(valid_filetypes.keys()))




    return image_data, calibration



"""
"""
def Extract_Profile(image_data):
    """
    Azimuthally integrates a 2D diffraction pattern

    Inputs:
       
       image_data  : np.array, the array of values in the image
       calibration : dictionary, the essential metadata to convert from pixels to two_theta space

    Outputs:
    

        1Dsignal: np.array, the array of values in the in pixel space

    """

    #Find the center of the 
    center = pfex.find_center(image_data)

    #Make Radial Profile based on the image dimensions
    pixel_range,brightness = pfex.radial_profile(image_data,center)

    """
    profile = {"pixel_range":pixel_range,
                "brightness":brightness}
    """
    return {"pixel_range":pixel_range,
                "brightness":brightness}



"""
"""
def Find_Peaks(profile,calibration):
    """
    Pulls out the peaks from a radial profile


    Inputs:

        profile  : np.array, the azimuthally integrated 2D diffraction pattern in pixel space.


    Outputs:

        peak_locs : list of arrays, two_theta and d_spacings of peaks in the profile
    """


    # find the location of the peaks in pixel space    
    peaks_pixel = pfnd.vote_peaks(profile["brightness"])
    

    #print(peaks_pixel[peaks_pixel>0])#DEBUG

    # convert pixel locations into d and two_theta positions
    peaks_theta, peaks_d = pfnd.pixel2theta(profile["pixel_range"][peaks_pixel>0],calibration['pixel_size'],
        calibration["camera_distance"],calibration["wavelength"])

    peaks_theta=peaks_theta[:4]

    #POSSIBLY IMPLEMENT CODE TO SHOW THE PEAKS FOUND FOR THE USER

    peak_locs = {"d_spacing":peaks_d,
                "2theta":[x for x in peaks_theta if x<90 and x >10],
                "vec":[int(2*x) for x in peaks_theta.tolist() if x < 90 and x > 10]
}


    pfnd.plot_peaks(profile['brightness'],profile["pixel_range"],peaks_pixel)

    return peak_locs

"""
"""
def Send_For_Classification(peak_locations,user_info,URL,fam=None):
    """
    Input:

    Outputs:
    
    Calls:

        POST(CLASSIFICATION_ENDPOINT):     

    """
    int_to_fam = {"0":"triclinic",
                  "1":"monoclinic",
                  "2":"orthorhombic",
                  "3":"tetragonal",
                  "4":"trigonal",
                  "5":"hexagonal",
                  "6":"cubic"}


    payload = {'peaks':peak_locations['vec'],
                'family':fam,
                'genus':None,
                'species':None
                }


    # if no family is provided then it tries to predict the family
    if fam is None:
        family = requests.post(URL+"predict/family", json=payload).text
        payload['family'] = int_to_fam[family]
        print(family)
        
    # Once the family is known, predicts the genus
    genus = requests.post(URL+"predict/genera", json=payload).text
    payload['genus'] = genus
    print(genus)

    # Once the genera are predicted give the top two from each
    species = requests.post(URL+"predict/species", json=payload).text
    payload['species'] = species

    return payload