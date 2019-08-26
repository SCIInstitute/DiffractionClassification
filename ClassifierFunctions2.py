import csv
import os
import numpy as np 

from matplotlib import pyplot as plt
from future.builtins.misc import input


def choose_peaks(peaks):
    """
    prompt user to select which peaks to classify on
    """
    d = peaks
     
    maximum = len(d)
    print(len(d))
    raw_choices =  input("Choose which peaks you'd like to select separated by spaces.\n").split(" ")

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
                "d_spacing":[d[i-1] for i in temp_choices],
                "2theta":[theta[i-1] for i in temp_choices],
                "vec":[vec[i-1] for i in temp_choices]
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


    schema = ["file_name","family","genus","species","peaks"]

    # if no file exists create a one and inform the user
    if not os.path.exists(path):
        print("creating new output file {}".format(path))
        with open(path, "wb") as csv_file:
            filewriter = csv.writer(csv_file, delimiter=",")
            filewriter.writerow(schema)

    row = []

    row.append(data_dict["file_name"])
    
    row.append(data_dict["family"])
    row.append(data_dict["genus"])
    row.append(data_dict["species"])
    
    row.append(data_dict["peaks"])

    with open(path, "ab") as csv_file:
        filewriter = csv.writer(csv_file, delimiter=",")
        filewriter.writerow(row)



