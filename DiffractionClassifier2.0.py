import ClientSide2 #custom package

import numpy as np
import argparse
import json
import os
import ClassifierFunctions2 as cf

from matplotlib import pyplot as plt
from builtins import input

    

# Initialize essential global variables
USER_INFO = "user_profile.json"
URL =  "http://ec2-34-214-102-24.us-west-2.compute.amazonaws.com/"#you'll need me to send you the link
#URL =  "http://ec2-34-219-165-244.us-west-2.compute.amazonaws.com/"#you'll need me to send you the link
#URL =  "http://ec2-54-218-209-196.us-west-2.compute.amazonaws.com/"
FAMILIES = ["triclinic","monoclinic","orthorhombic","tetragonal",
        "trigonal","hexagonal","cubic"]

DEFAULT_SESSION = os.path.join ("Sessions","session.json")


def build_parser():
    parser = argparse.ArgumentParser()

    # This will be implemented as rollout broadens
    parser.add_argument('--apikey', type=str,
                        dest='key', help='api key to securely access service',
                        metavar='KEY', required=False)

    parser.add_argument('--session',
                        dest='session',help='Keep user preferences for multirun sessions',
                        metavar='SESSION',required=False, default=None)
    return parser



def main():

    parser = build_parser()
    options = parser.parse_args()

    print(options.session)

    # opens the user specified session
    if options.session:
        with open(os.path.join("Sessions",options.session),'r') as f:
            session = json.load(f)

    # opens the default session    
    else:
        with open(DEFAULT_SESSION,'r') as f:

            session = json.load(f)

    # set variables from loaded session data
    file_path = session["file_path"]
    output_file = session["output_file"]

    manual_peak_selection = session["manual_peak_selection"]

    known_family = session["known_family"]

    if known_family and known_family=='yes':
        print('known family')
        crystal_family = session["crystal_family"]
    else:
        crystal_family = None
    
    # Load user from provided path, [IN PROGRESS]
    with open(USER_INFO) as f:
        user_info = json.load(f)
    
    # Determine if the path is a directory or a file
    if os.path.isdir(file_path):
        print("loading files from directory")
        file_paths = []
        for dirpath,dirnames,fpath in os.walk(file_path):
            for path in fpath:
                file_paths.append(os.path.join(dirpath,path))
        print("found {} files to load.".format(len(file_paths)))

    else:
        file_paths = [file_path]
    

    for f_path in file_paths:

        # Load Data from specified file (DM3, TIFF, CSV etc....)
        
        print("loading data from {}".format(f_path))
        image_data,scale = ClientSide2.Load_Profile(f_path)
        print("I successfully loaded the data")
        

        peak_locs = ClientSide2.Find_Peaks(image_data,scale)
        # Choose which peaks to classify on
        if manual_peak_selection:
            #peak_locs = cf.choose_peaks(peak_locs)
            raise NotImplementedError
        
        print(peak_locs)

            
        classificated = ClientSide2.Send_For_Classification(peak_locs,crystal_family,user_info,URL)

        classificated["file_name"] = f_path

        # update the user on the results before saving
        print(classificated)

        # write results out to the specified file
        cf.write_to_csv(os.path.join("Results",output_file),classificated)

if __name__ == "__main__":
    main()


