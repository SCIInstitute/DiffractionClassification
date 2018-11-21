import ClientSide #custom package

import numpy as np
import argparse
import json
import os
import ClassifierFunctions as cf

from matplotlib import pyplot as plt
from builtins import input

    

USER_INFO = "user_profile.json"
URL = "http://ec2-34-219-77-112.us-west-2.compute.amazonaws.com/"#you'll need me to send you the link
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
    file_path = session["file_path"]
    output_file = session["output_file"]
    is_profile = session["is_profile"]
    manual_peak_selection = session["manual_peak_selection"]
    scale_bar = session["scale_bar"]

    with open(USER_INFO) as f:
        user_info = json.load(f)


    #peak_locs = {"vec":[28,48,56, 61, 103, 124, 131]}
    peak_locs = {"vec":[95, 113, 153]}#CeO2


    print (peak_locs)

    if provide_family =="yes":
        while fam is None:
            temp_fam = input("What family does the Crystal belong to?\n")
            if temp_fam in FAMILIES:
                fam = temp_fam
            else:
                print("Invalid choice. choose from {}\n".format(str(FAMILIES)[1:-1]))

    classificated = ClientSide.Send_For_Classification(peak_locs,user_info,URL,fam)  

    classificated["file_name"] = "FAPbI-HTXRD-Sample2_FAPbI_I25_C1_145.0C.csv"

    print(classificated)

    # write results out to the specified file
    cf.write_to_csv(output_file,classificated)

if __name__ == "__main__":
    main()

