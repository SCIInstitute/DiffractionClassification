from __future__ import print_function
from __future__ import division


import ProfileExtraction as pfex #custom library to handle the functions behind Extract_Profile
import PeakFinding as pfnd #custom library to handle the functions behind Find_Peaks



import numpy as np

"""
"""
def Load_Image(path):
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
    valid_filetypes={".tif":tif_extract,
                    ".png":png_extract,
                    ".dm3":dm3_extract,
                    }
    
    file_type = path[-4:]

    # Check that the provided file is a supported file type
    if file_type in valid_filetypes.keys():
        
        # Call the appropriate extraction function
        valid_filetypes[file_type](file_type)

    else:

        raise ValueError("Unsupported file type: please submit a {}".format(valid_filetypes.keys()))



    # Open the file
    opened_file = None

    # extract the data
    image_data = opened_file.image_data #PLACEHOLDER
    metadata = opened_file.metadata #PLACEHOLDER

    # extract the metadata
    pixel_size,wavelength,camera_dist = metadata_extract(metadata)

    calibration = { "pixel_size":   float,
                    "wavelength":   float,
                    "camera_dist":  float}



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
    
    print(peaks_pixel[peaks_pixel>0])

    # convert pixel locations into d and two_theta positions
    peaks_d, peaks_theta = pfnd.pixel2theta(profile["pixel_range"][peaks_pixel>0],calibration['pixel_size'],
        calibration["camera_distance"],calibration["wavelength"])

    #POSSIBLY IMPLEMENT CODE TO SHOW THE PEAKS FOUND FOR THE USER

    peak_locs = {"d_spacing":peaks_d,
                "2theta":peaks_theta}


    pfnd.plot_peaks(profile['brightness'],profile["pixel_range"],peaks_pixel)

    return peak_locs

"""
"""
def Send_For_Classification(peak_locations):
    """
    Input:

    Outputs:
    
    Calls:

        POST(CLASSIFICATION_ENDPOINT):     

    """

    #response = CALL(CLASSIFICATION_ENDPOINT:peak_locations)
    response=None

    return response
