import ClientSide #custom package

import numpy as np
import argparse
import json
import os
from matplotlib import pyplot as plt
from future.builtins.misc import input

USER_INFO = "user_profile.json"
URL =  #you'll need me to send you the link
families = ["triclinic","monoclinic","orthorhombic","tetragonal",
        "trigonal","hexagonal","cubic"]

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', type=str,
                        dest='fpath', help='path to the image',
                        metavar='FPATH',default=None,required=False)

    parser.add_argument('--calibration', type=str,
                        dest='calibration', help='path to the calibration json',
                        metavar='calibration',default=None, required=False)

    parser.add_argument('--apikey', type=str,
                        dest='key', help='apikey to securely access service',
                        metavar='KEY', required=False)

    parser.add_argument('--is-profile',
                    dest='profile', help='set if the data will is an image or a profile',
                    default=False, action="store_true",required=False)


    return parser

def validate_calibration(prompt,name):
    while True:
        temp_value = input(prompt)
        try:
            float(temp_value)

            if temp_value > 0:
                return float(temp_value)
            else:
                print("invalid {}".format(name))
        except:
            print("invalid {}".format(name))

def validate_profile_choice(dims):

    if dims[0] > 1:
        profile_choice = int(input("Multiple profiles detected.\nplease choose which profile to use.\n"))
        while profile_choice not in range(dims[0]):
            profile_choice = int(input("Incorrect selection.\nplease choose {}.\n".format(range(dims[0]))))            
    else:
        profile_choice = 0


    return profile_choice

def main():
    parser = build_parser()
    options = parser.parse_args()
    if options.fpath is None:
        print("No path to data provided.\n Please enter filepath to your data")
        options.fpath = input()

    print("loading data from {}".format(options.fpath))
    image_data, calibration = ClientSide.Load_Image(options.fpath)
    calibrate = options.calibration 

    

    # Change the processing based on data type
    if options.profile==True:
        print("The data is a profile.")

        if len(image_data.shape) == 1:
            plt.plot(image_data)
            plt.show(block=False)            
        else:

            # show the user which profiles are present
            for i in range(image_data.shape[0]):
                plt.plot(image_data[i,:], label="profile {}".format(i))
            plt.legend()
            plt.show(block=False)

            # have the user select the profile
            profile_choice = validate_profile_choice(image_data.shape)
            image_data = image_data[profile_choice]
            # show chosen profile
            plt.plot(image_data)
            plt.show(block=False)
    else:
        plt.imshow(image_data)
        plt.show(block=False)

    # Load user configuration
    with open(USER_INFO) as f:
        user_info = json.load(f)

    #prompt user to provide calibration if none was found
    if calibrate is None:
        print("No calibration would be extracted from the file metadata\n Please enter calibration paramters")
        
        pixel_size = validate_calibration("Please enter a pixel size (in angstroms) e.g. 14.1\n","pixel_size")
        if not options.profile:     
            camera_dist = validate_calibration("Please enter camera distance from sample (in millimeters) e.g. 223.1\n","camera distance")
        else:
            camera_dist = 0
            
        wavelength = validate_calibration("Please enter beam wavelength (in microns) e.g. .02354\n","wavelength")            

        calibration = { "pixel_size":   pixel_size,
                "wavelength":   wavelength,
                "camera_distance":  camera_dist}
    else:
        print("Loading calibration from the specified file")
        with open(calibrate,'r') as f:
            calibration = json.load(f)

    # Change the Processing based on the type of data
    if options.profile==True:
        radial_profile = {"brightness":image_data,
                            "pixel_range":np.linspace(0,image_data.shape[0],image_data.shape[0])}

    else:
        radial_profile = ClientSide.Extract_Profile(image_data)    



    peak_locs = ClientSide.Find_Peaks(radial_profile,calibration,options.profile)

    print(peak_locs)

    if len(peak_locs) <= 2:
        print("WARNING: only {} peaks were detected, this is lower than the recommended 4+ peaks needed\nfor best results. Please check calibration.")

    fam = None
    provide_family = None
    while provide_family is None:
        temp_choice = input("Would you like to suggest a crystal family? yes or no\n")
        if temp_choice =="yes":
            provide_family = temp_choice
        elif temp_choice =="no":
            provide_family = temp_choice
        else:
            print("Invalid choice. Please choose yes or no\n")
    
    if provide_family =="yes":
        while fam is None:
            temp_fam = input("What family does the Crystal belong to?\n")
            if temp_fam in families:
                fam = temp_fam
            else:
                print("Invalid choice. choose from {}\n".format(str(families)[1:-1]))

    classificated = ClientSide.Send_For_Classification(peak_locs,user_info,URL,fam)  

    print(classificated)

if __name__ == "__main__":
    main()


