from __future__ import print_function
from __future__ import division


from Notation import SpaceGroupsDict as spgs

SpGr = spgs.spacegroups()

import ProfileExtraction as pfex #custom library to handle the functions behind Extract_Profile
import PeakFinding as pfnd #custom library to handle the functions behind Find_Peaks
import UniversalLoader as uvll #custom library to handle the functions behind UniversalLoader
import requests


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
                    ".csv":uvll.csv_extract,
                    ".txt":uvll.txt_extract}
    
    file_type = path[-4:]

    # Check that the provided file is a supported file type
    if file_type in valid_filetypes.keys():
        
        # Call the appropriate extraction function
        image_data =  valid_filetypes[file_type](path)

    else:

        raise ValueError("Unsupported file type: please use a {}".format(valid_filetypes.keys()))




    return image_data


def Extract_Profile(image_data):
    """
    Azimuthally integrates a 2D diffraction pattern

    Inputs:
       
       image_data  : np.array, the array of values in the image

    Outputs:
    

        profile: dictionary, contains intensity profile and pixel scale of
                                diffraction pattern

    """

    #Find the center of the 
    center = pfex.find_center(image_data)

    #Make Radial Profile based on the image dimensions
    pixel_range,brightness = pfex.radial_profile(image_data,center)


    return {"pixel_range":pixel_range,
                "brightness":brightness}



"""
"""
def Find_Peaks(profile,calibration,is_profile=False,display_type="d",scale_bar="pixel"):
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

    filter_size=max(int(profile["pixel_range"].shape[0]/50),3)
    
    # find the location of the peaks in pixel space    
    peaks_pixel = pfnd.vote_peaks(profile["brightness"],filter_size=filter_size)
    
    if is_profile:

        if scale_bar == "pixel":
            peaks_theta, peaks_d = pfnd.profile2theta(profile["pixel_range"][peaks_pixel>0],
                calibration['pixel_size'],calibration["wavelength"])
            scale_t, scale_d = pfnd.pixel2theta(profile["pixel_range"],calibration['pixel_size'],
                                        calibration["camera_distance"],calibration["wavelength"])

            print(peaks_theta,peaks_d)

        elif scale_bar == "d":

            peaks_theta = pfnd.d2theta(profile["pixel_range"][peaks_pixel>0],calibration["wavelength"])

            peaks_d = profile["pixel_range"][peaks_pixel>0]
            scale_t = pfnd.d2theta(profile["pixel_range"],calibration["wavelength"])
            scale_d = profile["pixel_range"]
            
            print(peaks_d)

        elif scale_bar =="theta":

            peaks_theta = peaks_pixel

        else:
            print("Invalid scale bar selection. Choose pixel or d")

    else:

        # convert pixel locations into d and two_theta positions
        peaks_theta, peaks_d = pfnd.pixel2theta(profile["pixel_range"][peaks_pixel>0],calibration['pixel_size'],
            calibration["camera_distance"],calibration["wavelength"])
        scale_t, scale_d = pfnd.pixel2theta(profile["pixel_range"],calibration['pixel_size'],
                                        calibration["camera_distance"],calibration["wavelength"])

    peak_locs = {"d_spacing":[x for x in peaks_d if x<10 and x >.9],
                "2theta":[x for x in peaks_theta if x<90 and x >10],
                "vec":[int(round(2*x)) for x in peaks_theta.tolist() if x < 90 and x > 10]
        }

    # Display the data on the selected scale bar
    if display_type == "d":
        pfnd.plot_peaks(profile['brightness'],scale_d,peaks_pixel,"d")

    elif display_type == "theta":
        pfnd.plot_peaks(profile['brightness'],scale_d,peaks_pixel,"theta")
    
    elif display_type == "both":
        pfnd.plot_peaks(profile['brightness'],scale_d,peaks_pixel,"d")
        pfnd.plot_peaks(profile['brightness'],scale_t,peaks_pixel,"theta")
    elif display_type == "none":
        pass
    else:
        print("Error invalid display_type")


    if len(peak_locs) <= 2:
        print("WARNING: only {} peaks were detected, this is lower than the recommended 4+ peaks needed\nfor best results. Please check calibration.")


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
                'genus_confidence':None,
                'First Prediction':None,
                'Second Prediction':None
                }


    # If no family is provided then it tries to predict the family
    if fam is None:
        family = requests.post(URL+"predict/family", json=payload).text
        payload['family'] = int_to_fam[family]
        print(payload['family'])
        print(requests.post(URL+"predict/family", json=payload).text)
        
        
    # Once the family is known, predicts the genus
    print(payload)
    print(requests.post(URL+"predict/genera", json=payload).text)
    genus = requests.post(URL+"predict/genera", json=payload).json()
    
    print(genus)

    payload['genus_1'] = genus["genus_1"]
    payload['genus_confidence_1'] = genus["genus_confidence_1"]
    payload['genus_2'] = genus["genus_2"]
    payload['genus_confidence_2'] = genus["genus_confidence_2"]

    # Once the genera are predicted give the top two from each
    print(payload)
    print(requests.post(URL+"predict/species", json=payload,timeout=30).text)
    species = requests.post(URL+"predict/species", json=payload,timeout=30).json()
    print(species)

    # Formatting the response to be saved more easily

    # First prediction
    payload["species_1"]=str(species["prediction1"][0])
    payload["confidence_1"]=str(float(species["prediction1"][1])*float(genus["genus_confidence_1"]))
    payload["hall_1"]=SpGr.sgs_to_group[str(species["prediction1"][0])]
    
    # Second prediction
    payload["species_2"]=str(species["prediction2"][0])
    payload["confidence_2"]=str(float(species["prediction2"][1])*float(genus["genus_confidence_1"]))
    payload["hall_2"]=SpGr.sgs_to_group[str(species["prediction2"][0])]

    # Third prediction  
    payload["species_3"]=str(species["prediction3"][0])
    payload["confidence_3"]=str(float(species["prediction3"][1])*float(genus["genus_confidence_2"]))
    payload["hall_3"]=SpGr.sgs_to_group[str(species["prediction3"][0])]
    
    # Fourth prediction  
    payload["species_4"]=str(species["prediction4"][0])
    payload["confidence_4"]=str(float(species["prediction4"][1])*float(genus["genus_confidence_2"]))
    payload["hall_4"]=SpGr.sgs_to_group[str(species["prediction4"][0])]

    return payload
