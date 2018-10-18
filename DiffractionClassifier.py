import ClientSide #custom package

import numpy as np
import argparse
import json
import os

import ClassifierFunctions as cf

from matplotlib import pyplot as plt
from future.builtins.misc import input


USER_INFO = "user_profile.json"
URL = "http://ec2-34-219-77-112.us-west-2.compute.amazonaws.com/"#you'll need me to send you the link
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

    parser.add_argument('--session',
                        dest='session',help='Keep user preferences for multirun sessions',
                        metavar='SESSION',required=False, default=None)


    return parser



def main():
    parser = build_parser()
    options = parser.parse_args()
    if options.fpath is None:
        print("No path to data provided.\n Please enter filepath to your data")
        options.fpath = input()

    print("loading data from {}".format(options.fpath))
    image_data, calibration = ClientSide.Load_Image(options.fpath)
    calibrate = options.calibration 

    if options.session:
        with open(options.session,'r') as f:
            session = json.load(f)
        fam = session["crystalfamily"]
        provide_family = session["known_family"]
        display_type = session["display_type"]
    
    else:
        fam = None
        provide_family = cf.provide_family()
        display_type = cf.choose_display()


    # Change the processing based on data type
    if options.profile==True:

        # Choose which profile if there are multiple
        cf.choose_profile(image_data)
    
    else:
        plt.imshow(image_data)
        plt.show(block=False)

    # Load user configuration from provided path
    with open(USER_INFO) as f:
        user_info = json.load(f)

    #prompt user to provide calibration if none was found
    if calibrate is None:

        calibration = cf.set_calibration(options.profile)

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


    peak_locs = ClientSide.Find_Peaks(radial_profile,calibration,options.profile,display_type)


    print (peak_locs)
    # Choose which peaks to classify on
    peak_locs = cf.choose_peaks(peak_locs,display_type)

    print (peak_locs)
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


