import csv
import os
import numpy as np
import time

from matplotlib import pyplot as plt
from future.builtins.misc import input


def choose_peaks(peaks,peak_h):
    """
    prompt user to select which peaks to classify on
    """
    d = peaks
    maximum = len(d['d_spacing'])

    plt.title('select peaks.  Enter to stop.')
    
    raw_choices = []
    while True:
        pts = []
        pts = plt.ginput(100, timeout=-1)
            
        print(pts)
        print(len(pts))
        
        index = []
        for p in pts:
            index.append(np.argmin(np.abs(d['d_spacing']-p[0])))
        
        index.sort()
    
        
        
        for i in index:
            peak_h[i][0].set_linewidth(5)
      
      
        plt.title('Enter to keep peaks, or reselect points')
        
#        time.sleep(1)  # Wait a second
        
        if plt.waitforbuttonpress():
            break
    
    
    
    #raw_choices =  input("Choose which peaks you'd like to select separated by spaces.\n").split(" ")
    
    raw_choices = index

    temp_choices = []

    for choice in raw_choices:
        try:
            temp_index = int(choice)
            if temp_index > 0 and temp_index <= maximum and temp_index not in temp_choices:
                temp_choices.append(temp_index)
            else:
                print("index {} outside of available peaks".format(temp_index))
        except:
            print("couldn't convert {} into an index".format(choice))

    print(temp_choices)

    
    temp_locs = {
                "d_spacing":[d['d_spacing'][i-1] for i in temp_choices],
                #"2theta":[theta[i-1] for i in temp_choices],
                "vec":[d['vec'][i-1] for i in temp_choices]
                }

    return temp_locs

def provide_family():
    """
    prompt user and ensure proper selection of base Crystal family
    """

    family = None

    while family is None:
        temp_choice = input("Would you like to suggest a crystal family? yes or no\n")

        if temp_choice =="yes":
            family = temp_choice
        elif temp_choice =="no":
            family = temp_choice
        else:
            print("Invalid choice. Please choose yes or no\n")

    return family


def write_to_csv(path,data_dict):
    """
    save new row of results to csv
    """


    schema = ["file_name","family","confidence", "genus 1st pred","confidence", "species_1", "confidence", "species_2", "confidence", "genus 2nd pred","confidence","species_3", "confidence", "species_4", "confidence", "peaks"]

    # if no file exists create a one and inform the user
    if not os.path.exists(path):
        print("creating new output file {}".format(path))
        with open(path, "w") as csv_file:
            filewriter = csv.writer(csv_file, delimiter=",")
            filewriter.writerow(schema)

    row = []

    row.append(data_dict["file_name"])
    row.append(data_dict["family"])
    row.append(data_dict["fam_confidence"])
    row.append(data_dict["genus_1"])
    row.append(data_dict["gen_confidence_1"])
    
    row.append(data_dict["species_1"])
    row.append(data_dict["spec_confidence_1"])
    row.append(data_dict["species_2"])
    row.append(data_dict["spec_confidence_2"])
    
    row.append(data_dict["genus_2"])
    row.append(data_dict["gen_confidence_2"])
    
    row.append(data_dict["species_3"])
    row.append(data_dict["spec_confidence_3"])
    row.append(data_dict["species_4"])
    row.append(data_dict["spec_confidence_4"])
    row.append(data_dict["peaks"])

    with open(path, "a") as csv_file:
        filewriter = csv.writer(csv_file, delimiter=",")
        filewriter.writerow(row)



