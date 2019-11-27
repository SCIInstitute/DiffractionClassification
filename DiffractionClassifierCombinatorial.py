import ClientSide as ClientSide #custom package

import numpy as np
import argparse
import json
import os
import ClassifierFunctions as cf
import csv
from matplotlib import pyplot as plt
from builtins import input

from Notation import SpaceGroupsDict as spgs
SpGr = spgs.spacegroups()

from itertools import combinations,chain



# Initialize essential global variables
USER_INFO = "user_profile.json"
#URL = "" # you'll need me to send you the link
SERVER_INFO = "server_gen1.json"
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


def powerset(iterable):
   "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
   s = list(iterable)
   return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
    
def write_to_csv(path,data_dict):
    schema = ["file_name","family","genus","genus_confidence",
           "species_1","confidence_1","hall_1",
           "species_2","confidence_2","hall_2",
           "species_3","confidence_3","hall_3",
           "species_4","confidence_4","hall_4","peaks"]    # if no file exists create a one and warn the user
    if not os.path.exists(path):
        print("creating new output file {}".format(path))
        with open(path, "w") as csv_file:
            filewriter = csv.writer(csv_file, delimiter=",")
            filewriter.writerow(schema)

    row = []
    row.append(data_dict["file_name"])
    row.append(data_dict["family"])

    row.append(data_dict["genus_1"])
    row.append(data_dict["genus_confidence_1"][:5])

    row.append(data_dict["species_1"])
    row.append(data_dict["confidence_1"][:5])
    row.append(data_dict["hall_1"])

    row.append(data_dict["species_2"])
    row.append(data_dict["confidence_2"][:5])
    row.append(data_dict["hall_2"])

    row.append(data_dict["species_3"])
    row.append(data_dict["confidence_3"][:5])
    row.append(data_dict["hall_3"])

    row.append(data_dict["species_4"])
    row.append(data_dict["confidence_4"][:5])
    row.append(data_dict["hall_4"])

    row.append(data_dict["peaks"])

    with open(path, "a") as csv_file:
        filewriter = csv.writer(csv_file, delimiter=",")
        filewriter.writerow(row)

def combination_peaks(peak_batch,temp_name,user_info,URL,fam):
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
                classificated = ClientSide.Send_For_Classification(combo,user_info,URL,fam)
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
        print("Loading calibration from {}".format(os.path.join("Calibrations",auto_calibrate)))  
        with open(os.path.join("Calibrations",auto_calibrate),'r') as f:
            calibration = json.load(f)

    except:
        print("No calibration could be loaded from {}\nPlease check the file exists and is formatted properly".format(auto_calibrate))
        calibration = cf.set_calibration(is_profile)
    print(calibration)

    with open(SERVER_INFO,'r') as f:
        server_info = json.load(f)
        
    if server_info['URL']:
        URL = server_info['URL']
    else:
        raise ValueError('you need to have the server URL provided to you')
        

    # Load user from provided path, [IN PROGRESS]
    with open(USER_INFO) as f:
        user_info = json.load(f)
    
    if not os.path.exists(file_path):
        print("The path provided could not be found. Please check your session file path")
        return

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
    
    print(file_paths)
    for f_path in file_paths:

        # Load Data from specified file (DM3, TIFF, CSV etc....)
        try:
            print("loading data from {}".format(f_path))
            image_data = ClientSide.Load_Image(f_path)
            print("I successfully loaded the data")
        except:
            print("Invalid file path given ({}).\n Please enter filepath to your data".format(f_path))
            options.fpath = input()

        # Change the processing based on data type
        if is_profile:

            # Choose which profile if there are multiple
            image_data,scale = cf.choose_profile(image_data)
        
        else:
            pass
            #plt.imshow(np.log(image_data))
            #plt.show(block=False)
            #plt.show()

        # Change the Processing based on the type of data
        if is_profile:
            print("identifying from profile")
            radial_profile = {"brightness":image_data,
                                "pixel_range":scale}

        else:
            radial_profile = ClientSide.Extract_Profile(image_data)    

       
        peak_locs = ClientSide.Find_Peaks(radial_profile,calibration,is_profile,display_type,scale_bar)
        print(peak_locs)

        
        # Choose which peaks to classify on
        if manual_peak_selection:
            peak_locs = cf.choose_peaks(peak_locs,display_type)


        if provide_family =="yes":

            while fam is None:
                temp_fam = input("What family does the Crystal belong to?\n")
                if temp_fam in FAMILIES:
                    fam = temp_fam
                else:
                    print("Invalid choice. choose from {}\n".format(str(FAMILIES)[1:-1]))
        elif provide_family == "no":
            fam = None
            
        print(peak_locs)

        with open(os.path.join("Results",f_path.split(os.sep)[-1][:-4]+".json"), "w") as o:
            o.write(json.dumps(peak_locs))                
        
        lower_gen = SpGr.edges["genus"][fam][0]
        upper_gen = SpGr.edges["genus"][fam][1]
        fam_range = range(SpGr.edges["species"][lower_gen][0],1+SpGr.edges["species"][upper_gen][1])
        
        common_peaks,guesses = combination_peaks(peak_locs,f_path.split(os.sep)[-1][:-4],user_info,URL,fam)
        
        plt.figure(figsize=(len(fam_range)//2,4))
        prev_histograms = []
        plots = []

        for rank in range(1,5):
            histo = np.histogram([int(g) for g in guesses["species_{}".format(rank)]],bins=fam_range)
            #histo[0] = histo[0]*(2-(rank/5.0))
           
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
        print("Results/"+f_path.split(os.sep)[-1][:-4]+"gen1.png")
        plt.savefig("Results/"+f_path.split(os.sep)[-1][:-4]+"_gen1.png")
        plt.show(block=False)


if __name__ == "__main__":
    main()



