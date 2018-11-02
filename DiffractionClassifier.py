import ClientSide #custom package

import numpy as np
import argparse
import json
import os
import ClassifierFunctions as cf

from matplotlib import pyplot as plt
from builtins import input

    

USER_INFO = "user_profile.json"
URL = #you'll need me to send you the link
FAMILIES = ["triclinic","monoclinic","orthorhombic","tetragonal",
        "trigonal","hexagonal","cubic"]

DEFAULT_SESSION = "session.json"

def build_parser():

    parser = argparse.ArgumentParser()

    parser.add_argument('--filepath', type=str,
                        dest='fpath', help='path to the image',
                        metavar='FPATH',default=None,required=False)

    parser.add_argument('--apikey', type=str,
                        dest='key', help='api key to securely access service',
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

    # opens the user specified session
    if options.session:
        with open(options.session,'r') as f:
            session = json.load(f)

    # opens the default session    
    else:
        with open(DEFAULT_SESSION,'r') as f:

            session = json.load(f)

    # set session data
    fam = session["crystal_family"]
    provide_family = session["known_family"]
    display_type = session["display_type"]
    auto_calibrate = session["auto_calibrate"]
    file_path = session["file_path"]
    output_file = session["output_file"]
    is_profile = session["is_profile"]
    manual_peak_selection = session["manual_peak_selection"]
    scale_bar = session["scale_bar"]

    # Load calibration from specified file (json)
    try:
        print("Loading calibration from {}".format(auto_calibrate))  
        with open(auto_calibrate,'r') as f:
            calibration = json.load(f)
    except:
        print("No calibration could be loaded from {}\nPlease check the file exists and is formatted properly".format(auto_calibrate))
        calibration = cf.set_calibration(options.profsile)
    print(calibration)
    # Load user configuration from provided path
    with open(USER_INFO) as f:
        user_info = json.load(f)

    # Determine if the path is a directory or a file
    if os.path.isdir(file_path):
        print("loading files from directory")
        file_paths = []
        for dirpath,dirnames,fpath in os.walk(file_path):
            for path in fpath:
                file_paths.append(os.path.join(dirpath,path))
        print(file_paths)

    else:
        file_paths = [file_path]

    print(file_paths)
    for f_path in file_paths:

        # Load Data from specified file (DM3, TIFF, CSV etc....)
        try:
            print("loading data from {}".format(f_path))
            image_data = ClientSide.Load_Image(f_path)
        except:
            print("Invalid file path given ({}).\n Please enter filepath to your data".format(f_path))
            options.fpath = input()

        # Change the processing based on data type
        if is_profile:

            # Choose which profile if there are multiple
            image_data,scale = cf.choose_profile(image_data)
        
        else:
            plt.imshow(np.log(image_data))
            plt.show(block=False)
            #plt.show()

        # Change the Processing based on the type of data
        if is_profile:
            print("identifying from profile")
            radial_profile = {"brightness":image_data,
                                "pixel_range":scale}

        else:
            radial_profile = ClientSide.Extract_Profile(image_data)    

        #print(radial_profile,calibration,is_profile,display_type)
        peak_locs = ClientSide.Find_Peaks(radial_profile,calibration,is_profile,display_type,scale_bar)


        
        # Choose which peaks to classify on
        if manual_peak_selection:
            peak_locs = cf.choose_peaks(peak_locs,display_type)


        print (peak_locs)

        if provide_family =="yes":
            while fam is None:
                temp_fam = input("What family does the Crystal belong to?\n")
                if temp_fam in FAMILIES:
                    fam = temp_fam
                else:
                    print("Invalid choice. choose from {}\n".format(str(FAMILIES)[1:-1]))

        classificated = ClientSide.Send_For_Classification(peak_locs,user_info,URL,fam)  

        classificated["file_name"] = f_path

        print(classificated)

        # write results out to the specified file
        cf.write_to_csv(output_file,classificated)

if __name__ == "__main__":
    main()


