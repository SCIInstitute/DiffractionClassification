import ClientSide #custom package
import argparse

# server communication
import json

from future.builtins.misc import input
import os


# TESTING IMPORTS
import numpy as np
from matplotlib import pyplot as plt

USER_INFO = "user_profile.json"
URL =  "http://ec2-52-26-77-17.us-west-2.compute.amazonaws.com/" #you'll need me to send you the link
families = ["triclinic","monoclinic","orthorhombic","tetragonal",
        "trigonal","hexagonal","cubic"]

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', type=str,
                        dest='fpath', help='path to the image',
                        metavar='FPATH', required=True)

    parser.add_argument('--calibration', type=str,
                        dest='calibration', help='path to the calibration json',
                        metavar='calibration',default=None, required=False)

    parser.add_argument('--apikey', type=str,
                        dest='key', help='apikey to securely access service',
                        metavar='KEY', required=False)

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


def main():
    parser = build_parser()
    options = parser.parse_args()

    print("loading data from {}".format(options.fpath))    
    image_data, calibration = ClientSide.Load_Image(options.fpath)
    calibrate = options.calibration 

    # Load user configuration
    with open(USER_INFO) as f:
        user_info = json.load(f)

    #prompt user to provide calibration if none was found
    if calibrate is None:
        print("No calibration would be extracted from the file metadata\n Please enter calibration paramters")
        
        pixel_size = validate_calibration("Please enter a pixel size (in angstroms) e.g. 14.1\n","pixel_size")
        camera_dist = validate_calibration("Please enter camera distance from sample (in millimeters) e.g. 223.1\n","camera distance")
        wavelength = validate_calibration("Please enter beam wavelength (in microns) e.g. .02354\n","wavelength")            

        calibration = { "pixel_size":   pixel_size,
                "wavelength":   wavelength,
                "camera_distance":  camera_dist}
    else:
        print("Loading calibration from the specified file")
        with open(calibrate,'r') as f:
            calibration = json.load(f)

    radial_profile = ClientSide.Extract_Profile(image_data)    

    peak_locs = ClientSide.Find_Peaks(radial_profile,calibration)

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


