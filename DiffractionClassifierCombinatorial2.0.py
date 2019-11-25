import ClientSide2 #custom package

import numpy as np
import argparse
import json
import os
import ClassifierFunctions2 as cf

from matplotlib import pyplot as plt
from builtins import input

    

# Initialize essential global variables
#URL =  "" #you'll need me to send you the link
FAMILIES = ["triclinic","monoclinic","orthorhombic","tetragonal",
        "trigonal","hexagonal","cubic"]

DEFAULT_SESSION = os.path.join ("Sessions","session.json")
DEFAULT_USER = "user_profile.json"
SERVER_INFO = "server_gen2.json"

# list of three, one per level
prediction_per_level = [1, 2, 2]


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

def combination_peaks(peak_batch, chem_vec, mode, temp_name, crystal_family, user_info, URL, fam, prediction_per_level):

    outpath = "Ready"
    find_valid_peaks = list(powerset(peak_batch["vec"]))
    find_valid_peaks = [item for item in find_valid_peaks if len(item) > 2 and len(item) < 6]
    print(len(find_valid_peaks),"valid peak combinations")

    valid_peaks_combinations = [{"vec":proto_combo} for proto_combo in find_valid_peaks]
    found = False
    threshold = 0
    guesses = {"species_1":[],
                "species_2":[],
                "species_3":[],
                "species_4":[]}

    common_peaks = []
    failed_combos = valid_peaks_combinations
    #peak_locs,user_info,URL,fam
    persistance = 0
    LIMIT = 3

    while len(failed_combos) > 0 and persistance < LIMIT:
        for combo in failed_combos:
            try:
                classificated = ClientSide2.Send_For_Classification(combo, chem_vec, mode, crystal_family, user_info, URL, prediction_per_level)
                print(classificated)
                classificated["file_name"] = temp_name
                write_to_csv(os.path.join(outpath,temp_name)+".csv",classificated)

                guesses['species_1'].append(classificated["species_1"])
                guesses['species_2'].append(classificated["species_2"])
                guesses['species_3'].append(classificated["species_3"])
                guesses['species_4'].append(classificated["species_4"])
                
                common_peaks.append(classificated["species_1"])
                common_peaks.append(classificated["species_2"])
                common_peaks.append(classificated["species_3"])
                common_peaks.append(classificated["species_4"])
                
                # remove the classified combination
                failed_combos.remove(combo)
            except KeyboardInterrupt:
                raise
            except:
                print("An error occured this combination was not classified.\nIt will be retried {} more times".format(LIMIT-persistance))

        persistance += 1

    if len(failed_combos)>0:
        print("there were {} failed combinations".format(len(failed_combos)))

    return common_peaks, guesses


def main():

    parser = build_parser()
    options = parser.parse_args()

    #print(options.session)

    # opens the user specified session
    if options.session:
        with open(os.path.join("Sessions",options.session),'r') as f:
            session = json.load(f)

    # opens the default session    
    else:
        with open(DEFAULT_SESSION,'r') as f:
            session = json.load(f)

    # set variables from loaded session data
#    print(session)
    file_path = session["file_path"]
    output_file = session["output_file"]
    manual_peak_selection = session["manual_peak_selection"]
    known_family = session["known_family"]
    chemistry = session["chemistry"]
    diffraction = session["diffraction"]
    
    mode = ""
    
    if diffraction:
        if chemistry:
            mode="DiffChem"
        else:
            mode="DiffOnly"
    else:
        if chemistry:
            raise ValueError('Running chemistry only predictions is currently not implemented')
        else:
            raise ValueError('Invalid prediction type. Either diffraction or chemistry must be enabled')

    if known_family and known_family=='yes':
        print('known family')
        crystal_family = session["crystal_family"]
        prediction_per_level[0] = 1
    else:
        crystal_family = None
    
    # Load user from provided path, [IN PROGRESS]
    if session["user_info"]:
        with open(session["user_info"],'r') as f:
            user_info = json.load(f)
    else:
        with open(DEFAULT_USER,'r') as f:
            user_info = json.load(f)
    
    with open(session["server_info"],'r') as f:
        server_info = json.load(f)
        
    if server_info['URL']:
        url = server_info['URL']
    else:
        raise ValueError('you need to have the server URL provided to you')
    
    chem_vec = cf.check_for_chemistry(session)
        
    
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
        
#        print(scale)

        if diffraction:
            peak_locs,peaks_h = ClientSide2.Find_Peaks(image_data,scale)
            # Choose which peaks to classify on
            if manual_peak_selection:
                peak_locs = cf.choose_peaks(peak_locs,peaks_h)
                #raise NotImplementedError
        else:
            peak_locs = []
            peaks_h = []
#        
#        print(peak_locs)
#        print(chem_vec)

        fam_range = range(1,231)
        
        common_peaks,guesses = combination_peaks(peak_locs, chem_vec, mode, f_path.split(os.sep)[-1][:-4], crystal_family, user_info, url, prediction_per_level)

        plt.figure(figsize=(len(fam_range)//2,4))
        prev_histograms = []
        plots = []
        
        for rank in range(1,5):
            histo = np.histogram([int(g) for g in guesses["species_{}".format(rank)]],bins=fam_range)
            
            if rank > 1:
                plot = plt.bar(histo[1][:-1],histo[0],
                    bottom=np.sum(np.vstack(prev_histograms),axis=0),align="center")
            else:
                plot = plt.bar(histo[1][:-1],histo[0],align="center",color='red')
                
            plots.append(plot)
            plt.yticks(rotation='vertical')
            plt.xticks(histo[1][:-1],rotation='vertical')
            prev_histograms.append(histo[0])

        plt.xlabel("Prediction",fontsize=10,rotation='vertical')
        plt.ylabel("Counts",fontsize=10)
        #plt.legend(plots,("species_1","species_2","species_3","species_4"))
        plt.savefig("Results/"+f_path.split(os.sep)[-1][:-4]+".png")
        plt.show(block=False)
            
#        classificated = ClientSide2.Send_For_Classification(peak_locs, chem_vec, mode, crystal_family, user_info, url, prediction_per_level)
#
#        classificated["file_name"] = f_path
#
#        # update the user on the results before saving
#        print(classificated)
#
#        # write results out to the specified file
#        cf.write_to_csv(os.path.join("Results",output_file), classificated, prediction_per_level)

if __name__ == "__main__":
    main()


