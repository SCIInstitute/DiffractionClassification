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
    peaks_h = pfnd.plot_peaks(profile[squished_scale],scale[squished_scale],peaks)

    if len(peak_locs['vec']) <= 2:
        print("WARNING: only {} peaks were detected," + 
            " this is lower than the recommended 4+ peaks needed"+
            "\nfor best results. Please check calibration.".format(len(peaks_d)))


    return peak_locs, peaks_h

def find_name_in_dict(name,dict):
    o_ind = False
    for ind, nm in dict.items():
        if nm == name:
            o_ind = ind

    return o_ind



def Send_For_Classification(peak_locations, crystal_family, user_info, URL, prediction_per_level, fam=None):
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

    print(payload)
    
    payload['prediction_per_level'] = prediction_per_level

    skip_family = False
    # reproduce the gen 1 ability to specify the family to look it.  Use this if the family prediction seems suspect.
    if crystal_family:
        print(" setting the family to search in is old functionality that is no longer needed for most predictions")
        number = find_name_in_dict(crystal_family,int_to_fam)
        if number:
            payload['family'] = crystal_family
            payload['family_1'] = crystal_family
            payload['fam_confidence_1'] = float("nan")
                
            
            payload['number'] = number+1
            skip_family = True
            
            payload = Classify_Family(peak_locations,payload,user_info,URL,1)
            
            for k in range(1,prediction_per_level):
                payload['family_'+str(1+k)] = float("nan")
                payload['fam_confidence_'+str(1+k)] = float("nan")
                
                for l in range(1,prediction_per_level):
                    num_l = (k-1)*prediction_per_level+l+1
                    payload['genus_'+str(num_l)] = float("nan")
                    payload['gen_confidence_'+str(num_l)] = float("nan")
                    
                    for m in range(1,prediction_per_level):
                        payload['genus_'+str(1+k)] = float("nan")
                        payload['gen_confidence_'+str(1+k)] = float("nan")
                    
            
            
        else:
            print("family name not recognized, ignoring input.")

    if not skip_family:
        print(requests.post(URL+"predict", json=payload).text)
        family = requests.post(URL+"predict", json=payload).json()
        print(family['votes'])
        fam_votes = family['votes']
        pred = []
#        pred.append(np.argmax(family['votes']))
#        payload['family_1'] = int_to_fam[pred[0]]
        fam_confidence = confidence(fam_votes)
#        payload['fam_confidence_1'] = fam_confidence[pred[0]]
#        payload['number'] = int(pred[0])+1
#
#        print(pred[0])
#        Classify_Family(peak_locations,payload,user_info,URL,1)
        print(fam_confidence)
        print(payload)
        
        for k in range(prediction_per_level):
            pred.append(np.argmax(fam_votes))
            payload['family'] = int_to_fam[pred[k]]
            payload['family_'+str(k+1)] = int_to_fam[pred[k]]
            payload['fam_confidence_'+str(k+1)] =fam_confidence[pred[k]]
            payload['number'] = int(pred[k])+1
            payload = Classify_Family(peak_locations,payload,user_info,URL,k+1)
            
            # for next iteration
            fam_votes[pred[k-1]] = -float("inf")
            
            
    return payload

    
def confidence(array):
    # softmax like normalization
    np_array = np.array(array)
        
    total = np.sum(np.exp(np_array))
    
#    print('softmax -')
#    print(np_array)
#    print(total)
#    print(np.exp(np_array)/total)

    #L = -np_array+np.log(total)
    #L = -np.log(np.exp(np_array)/total)
    L = np.exp(np_array)/total
#    L = np_array/np.sum(np_array)
    
    return L
    
def Classify_Family(peak_locations,payload,user_info,URL,pred_number):

    payload['level'] = "Genera"
        
    # Once the family is known, predicts the genus
    print(requests.post(URL+"predict", json=payload,timeout=30))
    genus = requests.post(URL+"predict", json=payload,timeout=30).json()

    print("---genus---")
    print(genus['votes'])
    
#    genera_votes = np.sum(genus['votes'],axis=0).tolist()
#    genera_votes_1 = int(np.argmax(genus['votes']))
    genera_votes = genus['votes']
    genera_con = confidence(genera_votes)
    pred=[]
    genera_pred = []
    
    for k in range(payload['prediction_per_level']):
        pred.append(int(np.argmax(genera_votes)))
        print(pred[k])
        g_pred_num = (pred_number-1)*payload['prediction_per_level']+k+1
        genera_pred.append(pred[k]+ notation_dictionary.edges["genus"][payload['family']][0])
        payload['genus_'+str(g_pred_num)] = genera_pred[k]
        payload['gen_confidence_'+str(g_pred_num)] = genera_con[pred[k]]
        
        payload['number'] = genera_pred[k]
        print('genus prediction = ',genera_pred[k])
        print('genus_number = ',g_pred_num)
        payload = Classify_Genus(peak_locations,payload,user_info,URL,g_pred_num)
   
        genera_votes[pred[k]] = - float("inf")
        print(genera_votes)
        
    return payload
    
#    pred_2 = int(np.argmax(genera_votes))
#    genera_pred_2 =  pred_2+ notation_dictionary.edges["genus"][payload['family']][0]
#
#
#    payload['genus_2'] = genera_pred_2
#    payload['gen_confidence_2'] = genera_con[pred_2]
    
    # Configure payload json for next request
    
    
    
    
    

def Classify_Genus(peak_locations,payload,user_info,URL,pred_number):

    # species prediction 1
    print("---species first genus---")
    payload['level'] = "Species"
    
    print(requests.post(URL+"predict", json=payload,timeout=30))
    species = requests.post(URL+"predict", json=payload,timeout=30).json()

    print(species)


    print(species['votes'])

    # Formatting the response to be saved more easily
    species_votes = species['votes']
    spec_confidence = confidence(species_votes)
    pred = []
    species_pred = []
    
    print(payload)
    
    for k in range(payload['prediction_per_level']):
        pred.append(int(np.argmax(species_votes)))
        species_pred.append(pred[k] + notation_dictionary.edges["species"][payload['genus_'+str(pred_number)]][0])
        num = (pred_number-1)*payload['prediction_per_level']+k+1
        print('species number = ',num)
        payload["species_"+str(num)] = species_pred[k]
        payload["spec_confidence_"+str(num)] = spec_confidence[pred[k]]

        species_votes[pred[0]] = -float("inf")
        
    return payload
        
#    pred_2 = int(np.argmax(species1_votes))
#    species_pred_2 = pred_2 + notation_dictionary.edges["species"][payload['genus_'+str(pred_number)]][0]

    # First prediction
#    payload["species_1"] = species_pred_1
#    payload["spec_confidence_1"] = spec1_confidence[pred_1]
#    payload["species_2"] = species_pred_2
#    payload["spec_confidence_2"] = spec1_confidence[pred_2]


    
    
